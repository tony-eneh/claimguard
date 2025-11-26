import {
  createWalletClient,
  createPublicClient,
  http,
  parseEther,
  Hash,
  keccak256,
  toBytes,
  defineChain,
} from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { config, validateConfig } from './config';
import fs from 'fs';
import path from 'path';

// Define Hardhat local network chain
const hardhatLocal = defineChain({
  id: 31337,
  name: 'Hardhat Local',
  nativeCurrency: {
    decimals: 18,
    name: 'Ether',
    symbol: 'ETH',
  },
  rpcUrls: {
    default: {
      http: ['http://127.0.0.1:8545'],
    },
  },
});

// Must match Solidity enums
enum Role {
  NONE,
  DRIVER,
  INSURER,
  REINSURER,
  ADJUSTER,
  POLICE,
  COURT,
  GARAGE,
  REGULATOR,
  CLOUD_PROVIDER,
}

enum ResourceType {
  GENERIC,
  FNOL,
  MEDICAL_REPORT,
  REPAIR_ESTIMATE,
  POLICE_REPORT,
  IMAGE,
  VIDEO,
  PDF,
  TELEMATICS,
  LOG,
  OTHER,
}

enum Action {
  READ,
  APPEND,
  UPDATE,
  DELETE,
  APPROVE,
  SHARE,
}

// Helper to convert string to bytes32
function stringToBytes32(str: string): Hash {
  return keccak256(toBytes(str));
}

async function main() {
  validateConfig();

  // Create public client for reading
  const publicClient = createPublicClient({
    chain: hardhatLocal,
    transport: http(config.rpcUrl),
  });

  // Create wallet client for writing
  const account = privateKeyToAccount(
    config.gatewayPrivateKey as `0x${string}`
  );
  const walletClient = createWalletClient({
    account,
    chain: hardhatLocal,
    transport: http(config.rpcUrl),
  });

  console.log('Seeding with signer:', account.address);

  // Get initial nonce
  const startNonce = await publicClient.getTransactionCount({
    address: account.address,
  });
  console.log('Starting nonce:', startNonce);

  // Contract ABIs
  const subjectRegistryAbi = [
    {
      name: 'setSubjectAttributes',
      type: 'function',
      stateMutability: 'nonpayable',
      inputs: [
        { name: 'subject', type: 'address' },
        { name: 'role', type: 'uint8' },
        { name: 'orgId', type: 'bytes32' },
        { name: 'jurisdiction', type: 'bytes32' },
        { name: 'isActive', type: 'bool' },
      ],
      outputs: [],
    },
  ] as const;

  const evidenceRegistryAbi = [
    {
      name: 'registerResource',
      type: 'function',
      stateMutability: 'nonpayable',
      inputs: [
        { name: 'contentHash', type: 'bytes32' },
        { name: 'uri', type: 'string' },
        { name: 'caseId', type: 'bytes32' },
        { name: 'rType', type: 'uint8' },
        { name: 'sensitivity', type: 'uint8' },
      ],
      outputs: [{ name: 'resourceId', type: 'uint256' }],
    },
  ] as const;

  const accessPolicyManagerAbi = [
    {
      name: 'createPolicy',
      type: 'function',
      stateMutability: 'nonpayable',
      inputs: [
        { name: 'role', type: 'uint8' },
        { name: 'orgId', type: 'bytes32' },
        { name: 'jurisdiction', type: 'bytes32' },
        { name: 'rType', type: 'uint8' },
        { name: 'caseId', type: 'bytes32' },
        { name: 'action', type: 'uint8' },
        { name: 'maxSensitivity', type: 'uint8' },
        { name: 'notBefore', type: 'uint64' },
        { name: 'notAfter', type: 'uint64' },
        { name: 'allow', type: 'bool' },
      ],
      outputs: [{ name: 'policyId', type: 'uint256' }],
    },
  ] as const;

  // ---------------------------------------------------------------------------
  // 1. Define orgIds and jurisdictions
  // ---------------------------------------------------------------------------
  const ORG_INSURER_A = stringToBytes32('INSURER_A');
  const ORG_INSURER_B = stringToBytes32('INSURER_B');
  const ORG_POLICE_KR = stringToBytes32('POLICE_KR');
  const ORG_COURT_KR = stringToBytes32('COURT_KR');
  const ORG_GARAGE_A = stringToBytes32('GARAGE_A');
  const ORG_REGULATOR_KR = stringToBytes32('REGULATOR_KR');

  const JUR_KR = stringToBytes32('KR_NATIONAL');
  const JUR_NG = stringToBytes32('NG_NATIONAL');

  // ---------------------------------------------------------------------------
  // 2. Generate subjects (200)
  // ---------------------------------------------------------------------------
  const totalSubjects = 200;
  const subjects: {
    address: `0x${string}`;
    role: Role;
    orgId: Hash;
    jur: Hash;
  }[] = [];

  // Simple helper to push subjects
  function addSubjects(count: number, role: Role, orgId: Hash, jur: Hash) {
    for (let i = 0; i < count; i++) {
      const wallet = privateKeyToAccount(
        keccak256(toBytes(`subject-${role}-${i}-${Date.now()}`))
      );
      subjects.push({
        address: wallet.address,
        role,
        orgId,
        jur,
      });
    }
  }

  // Using the role mix described earlier
  addSubjects(40, Role.INSURER, ORG_INSURER_A, JUR_KR);
  addSubjects(40, Role.INSURER, ORG_INSURER_B, JUR_KR);
  addSubjects(40, Role.ADJUSTER, ORG_INSURER_A, JUR_KR);
  addSubjects(30, Role.POLICE, ORG_POLICE_KR, JUR_KR);
  addSubjects(20, Role.COURT, ORG_COURT_KR, JUR_KR);
  addSubjects(20, Role.GARAGE, ORG_GARAGE_A, JUR_KR);
  addSubjects(10, Role.REGULATOR, ORG_REGULATOR_KR, JUR_KR);

  if (subjects.length !== totalSubjects) {
    console.warn(
      `Generated ${subjects.length} subjects (not exactly 200, but fine).`
    );
  }

  console.log(`Seeding ${subjects.length} subjects...`);

  const subjectsData: Array<{
    index: number;
    address: string;
    role: string;
    orgId: string;
    jurisdiction: string;
  }> = [];

  for (let i = 0; i < subjects.length; i++) {
    const s = subjects[i];

    const hash = await walletClient.writeContract({
      address: config.subjectAttributeRegistryAddress as `0x${string}`,
      abi: subjectRegistryAbi,
      functionName: 'setSubjectAttributes',
      args: [s.address, s.role, s.orgId, s.jur, true],
    });

    await publicClient.waitForTransactionReceipt({ hash });

    // Store subject data
    subjectsData.push({
      index: i,
      address: s.address,
      role: Role[s.role],
      orgId: s.orgId,
      jurisdiction: s.jur,
    });

    if ((i + 1) % 50 === 0) {
      console.log(`  -> ${i + 1}/${subjects.length} subjects registered`);
    }
  }
  console.log('Subjects seeded.');

  // Create outputs directory if it doesn't exist
  const outputsDir = path.join(process.cwd(), 'outputs');
  if (!fs.existsSync(outputsDir)) {
    fs.mkdirSync(outputsDir, { recursive: true });
  }

  // Save subjects to file
  const subjectsFile = path.join(outputsDir, 'subjects.json');
  fs.writeFileSync(subjectsFile, JSON.stringify(subjectsData, null, 2));
  console.log(`Subjects data saved to ${subjectsFile}`);

  // ---------------------------------------------------------------------------
  // 3. Generate resources (1000)
  // ---------------------------------------------------------------------------
  const totalResources = 1000;
  const numCases = 200;

  console.log(`Seeding ${totalResources} resources...`);

  // helper to choose resource type based on index
  function pickResourceType(i: number): ResourceType {
    const ratio = i / totalResources;
    if (ratio < 0.25) return ResourceType.VIDEO; // 0–249
    if (ratio < 0.5) return ResourceType.IMAGE; // 250–499
    if (ratio < 0.7)
      return Math.random() < 0.5
        ? ResourceType.FNOL
        : ResourceType.MEDICAL_REPORT; // 500–699
    if (ratio < 0.85) return ResourceType.TELEMATICS; // 700–849
    return ResourceType.OTHER; // 850–999
  }

  function pickSensitivity(rType: ResourceType): number {
    switch (rType) {
      case ResourceType.MEDICAL_REPORT:
        return 5;
      case ResourceType.FNOL:
        return 4;
      case ResourceType.VIDEO:
      case ResourceType.IMAGE:
        return 2;
      case ResourceType.TELEMATICS:
        return 3;
      default:
        return 1;
    }
  }

  const resourcesData: Array<{
    resourceId: number;
    caseIdHex: string;
    caseLabel: string;
    rType: string;
    sensitivity: number;
    uri: string;
  }> = [];

  for (let i = 0; i < totalResources; i++) {
    const caseIndex = i % numCases;
    const caseIdStr = `CASE_${caseIndex.toString().padStart(4, '0')}`;
    const caseId = stringToBytes32(caseIdStr);

    const rType = pickResourceType(i);
    const sensitivity = pickSensitivity(rType);

    // Fake URI and hash
    const uri = `s3://claimguard/case-${caseIndex}/${rType}-${i}.bin`;
    const hashInput = `${uri}-${Date.now()}-${Math.random()}`;
    const contentHash = stringToBytes32(hashInput);

    const hash = await walletClient.writeContract({
      address: config.evidenceRegistryAddress as `0x${string}`,
      abi: evidenceRegistryAbi,
      functionName: 'registerResource',
      args: [contentHash, uri, caseId, rType, sensitivity],
    });

    const receipt = await publicClient.waitForTransactionReceipt({ hash });

    // The resource ID is the return value, which starts from 1
    const resourceId = i + 1;

    // Store resource data
    resourcesData.push({
      resourceId,
      caseIdHex: caseId,
      caseLabel: caseIdStr,
      rType: ResourceType[rType],
      sensitivity,
      uri,
    });

    if ((i + 1) % 100 === 0) {
      console.log(`  -> ${i + 1}/${totalResources} resources registered`);
    }
  }
  console.log('Resources seeded.');

  // Save resources to file
  const resourcesFile = path.join(outputsDir, 'resources.json');
  fs.writeFileSync(resourcesFile, JSON.stringify(resourcesData, null, 2));
  console.log(`Resources data saved to ${resourcesFile}`);

  // ---------------------------------------------------------------------------
  // 4. Create ABAC policies
  // ---------------------------------------------------------------------------
  console.log('Creating ABAC policies...');

  const now = Math.floor(Date.now() / 1000);
  const oneMonth = 30 * 24 * 60 * 60;

  async function createPolicy(
    role: Role,
    orgId: Hash,
    jur: Hash,
    rType: ResourceType,
    caseId: Hash,
    action: Action,
    maxSensitivity: number,
    notBefore: number,
    notAfter: number,
    allow: boolean
  ) {
    const hash = await walletClient.writeContract({
      address: config.accessPolicyManagerAddress as `0x${string}`,
      abi: accessPolicyManagerAbi,
      functionName: 'createPolicy',
      args: [
        role,
        orgId,
        jur,
        rType,
        caseId,
        action,
        maxSensitivity,
        BigInt(notBefore),
        BigInt(notAfter),
        allow,
      ],
    });

    const receipt = await publicClient.waitForTransactionReceipt({ hash });
    console.log(
      `  Policy created for role=${Role[role]} action=${Action[action]} (gas used: ${receipt.gasUsed})`
    );
  }

  const ZERO_HASH: Hash = '0x0000000000000000000000000000000000000000000000000000000000000000';

  // 1) Insurers: READ all types, any case, any sensitivity
  await createPolicy(
    Role.INSURER,
    ZERO_HASH,
    ZERO_HASH,
    ResourceType.GENERIC,
    ZERO_HASH,
    Action.READ,
    5,
    0,
    0,
    true
  );

  // 2) Adjusters: READ, APPEND, UPDATE, sensitivity <= 4
  await createPolicy(
    Role.ADJUSTER,
    ZERO_HASH,
    ZERO_HASH,
    ResourceType.GENERIC,
    ZERO_HASH,
    Action.READ,
    4,
    0,
    0,
    true
  );
  await createPolicy(
    Role.ADJUSTER,
    ZERO_HASH,
    ZERO_HASH,
    ResourceType.GENERIC,
    ZERO_HASH,
    Action.APPEND,
    4,
    0,
    0,
    true
  );
  await createPolicy(
    Role.ADJUSTER,
    ZERO_HASH,
    ZERO_HASH,
    ResourceType.GENERIC,
    ZERO_HASH,
    Action.UPDATE,
    4,
    0,
    0,
    true
  );

  // 3) Police: READ VIDEO + IMAGE, sensitivity <= 3, time-bounded
  await createPolicy(
    Role.POLICE,
    ORG_POLICE_KR,
    JUR_KR,
    ResourceType.VIDEO,
    ZERO_HASH,
    Action.READ,
    3,
    now,
    now + oneMonth,
    true
  );
  await createPolicy(
    Role.POLICE,
    ORG_POLICE_KR,
    JUR_KR,
    ResourceType.IMAGE,
    ZERO_HASH,
    Action.READ,
    3,
    now,
    now + oneMonth,
    true
  );

  // 4) Court: READ all types, any case, sensitivity <= 5
  await createPolicy(
    Role.COURT,
    ORG_COURT_KR,
    JUR_KR,
    ResourceType.GENERIC,
    ZERO_HASH,
    Action.READ,
    5,
    0,
    0,
    true
  );

  // 5) Garage: READ IMAGE + REPAIR_ESTIMATE, sensitivity <= 2
  await createPolicy(
    Role.GARAGE,
    ORG_GARAGE_A,
    JUR_KR,
    ResourceType.IMAGE,
    ZERO_HASH,
    Action.READ,
    2,
    0,
    0,
    true
  );
  await createPolicy(
    Role.GARAGE,
    ORG_GARAGE_A,
    JUR_KR,
    ResourceType.REPAIR_ESTIMATE,
    ZERO_HASH,
    Action.READ,
    2,
    0,
    0,
    true
  );

  // 6) Regulator: READ all, max sensitivity
  await createPolicy(
    Role.REGULATOR,
    ORG_REGULATOR_KR,
    JUR_KR,
    ResourceType.GENERIC,
    ZERO_HASH,
    Action.READ,
    5,
    0,
    0,
    true
  );

  console.log('Seeding complete.');
}

main().catch((err) => {
  console.error('Seed error:', err);
  process.exit(1);
});
