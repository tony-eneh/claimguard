import { ethers } from 'ethers';
import { config, validateConfig } from './config';
import { createProvider, createSigner, getContracts } from './blockchain';

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

async function main() {
  validateConfig();

  const provider = createProvider();
  const signer = createSigner(provider);
  const { apm, evidenceReg, subjectReg } = getContracts(signer);

  const signerAddress = await signer.getAddress();
  console.log('Seeding with signer:', signerAddress);
  
  // Get initial nonce and wait a bit to ensure blockchain state is settled
  const startNonce = await provider.getTransactionCount(signerAddress, 'latest');
  console.log('Starting nonce:', startNonce);
  await new Promise(resolve => setTimeout(resolve, 1000));

  // ---------------------------------------------------------------------------
  // 1. Define orgIds and jurisdictions
  // ---------------------------------------------------------------------------
  const ORG_INSURER_A = ethers.id('INSURER_A');
  const ORG_INSURER_B = ethers.id('INSURER_B');
  const ORG_POLICE_KR = ethers.id('POLICE_KR');
  const ORG_COURT_KR = ethers.id('COURT_KR');
  const ORG_GARAGE_A = ethers.id('GARAGE_A');
  const ORG_REGULATOR_KR = ethers.id('REGULATOR_KR');

  const JUR_KR = ethers.id('KR_NATIONAL');
  const JUR_NG = ethers.id('NG_NATIONAL');

  // ---------------------------------------------------------------------------
  // 2. Generate subjects (200)
  // ---------------------------------------------------------------------------
  const totalSubjects = 200;
  const subjects: {
    address: string;
    role: Role;
    orgId: string;
    jur: string;
  }[] = [];

  // Simple helper to push subjects
  function addSubjects(count: number, role: Role, orgId: string, jur: string) {
    for (let i = 0; i < count; i++) {
      const wallet = ethers.Wallet.createRandom();
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

  for (let i = 0; i < subjects.length; i++) {
    const s = subjects[i];

    // Let ethers manage the nonce automatically
    const tx = await subjectReg.setSubjectAttributes(
      s.address,
      s.role,
      s.orgId,
      s.jur,
      true
    );
    await tx.wait();
    
    if ((i + 1) % 50 === 0) {
      console.log(`  -> ${i + 1}/${subjects.length} subjects registered`);
    }
  }
  console.log('Subjects seeded.');

  // Optionally: write subjects to a JSON file for your load generator
  // (do it later using fs if you want).

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

  for (let i = 0; i < totalResources; i++) {
    const caseIndex = i % numCases;
    const caseIdStr = `CASE_${caseIndex.toString().padStart(4, '0')}`;
    const caseId = ethers.id(caseIdStr);

    const rType = pickResourceType(i);
    const sensitivity = pickSensitivity(rType);

    // Fake URI and hash
    const uri = `s3://claimguard/case-${caseIndex}/${rType}-${i}.bin`;
    const hashInput = `${uri}-${Date.now()}-${Math.random()}`;
    const contentHash = ethers.id(hashInput); // keccak256

    // Let ethers manage the nonce automatically
    const tx = await evidenceReg.registerResource(
      contentHash,
      uri,
      caseId,
      rType,
      sensitivity
    );
    await tx.wait();

    if ((i + 1) % 100 === 0) {
      console.log(`  -> ${i + 1}/${totalResources} resources registered`);
    }
  }
  console.log('Resources seeded.');

  // ---------------------------------------------------------------------------
  // 4. Create ABAC policies
  // ---------------------------------------------------------------------------
  console.log('Creating ABAC policies...');

  const now = Math.floor(Date.now() / 1000);
  const oneMonth = 30 * 24 * 60 * 60;

  async function createPolicy(
    role: Role,
    orgId: string,
    jur: string,
    rType: ResourceType,
    caseId: string,
    action: Action,
    maxSensitivity: number,
    notBefore: number,
    notAfter: number,
    allow: boolean
  ) {
    // Let ethers manage the nonce automatically
    const tx = await apm.createPolicy(
      role,
      orgId,
      jur,
      rType,
      caseId,
      action,
      maxSensitivity,
      notBefore,
      notAfter,
      allow
    );
    const receipt = await tx.wait();
    console.log(
      `  Policy created for role=${Role[role]} action=${
        Action[action]
      } (gas used: ${receipt?.gasUsed?.toString()})`
    );
  }

  // 1) Insurers: READ all types, any case, any sensitivity
  await createPolicy(
    Role.INSURER,
    ethers.ZeroHash, // any org
    ethers.ZeroHash, // any jurisdiction
    ResourceType.GENERIC,
    ethers.ZeroHash, // any case
    Action.READ,
    5,
    0,
    0,
    true
  );

  // 2) Adjusters: READ, APPEND, UPDATE, sensitivity <= 4
  await createPolicy(
    Role.ADJUSTER,
    ethers.ZeroHash,
    ethers.ZeroHash,
    ResourceType.GENERIC,
    ethers.ZeroHash,
    Action.READ,
    4,
    0,
    0,
    true
  );
  await createPolicy(
    Role.ADJUSTER,
    ethers.ZeroHash,
    ethers.ZeroHash,
    ResourceType.GENERIC,
    ethers.ZeroHash,
    Action.APPEND,
    4,
    0,
    0,
    true
  );
  await createPolicy(
    Role.ADJUSTER,
    ethers.ZeroHash,
    ethers.ZeroHash,
    ResourceType.GENERIC,
    ethers.ZeroHash,
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
    ethers.ZeroHash,
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
    ethers.ZeroHash,
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
    ethers.ZeroHash,
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
    ethers.ZeroHash,
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
    ethers.ZeroHash,
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
    ethers.ZeroHash,
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
