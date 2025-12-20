import { ethers } from 'ethers';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Deploy ClaimGuard contracts to Sepolia testnet
 * For E2: Realistic Blockchain / Network Conditions
 */

async function main() {
  console.log("\n" + "=".repeat(80));
  console.log("SEPOLIA DEPLOYMENT: ClaimGuard Contracts");
  console.log("=".repeat(80) + "\n");

  // Connect to Sepolia
  const sepoliaRpcUrl = process.env.SEPOLIA_RPC_URL || 'https://sepolia.drpc.org';
  const privateKey = process.env.SEPOLIA_PRIVATE_KEY;
  
  if (!privateKey) {
    throw new Error("SEPOLIA_PRIVATE_KEY environment variable is required");
  }
  
  const provider = new ethers.JsonRpcProvider(sepoliaRpcUrl);
  const deployer = new ethers.Wallet(privateKey, provider);
  
  console.log('Deploying contracts with account:', deployer.address);
  const balance = await provider.getBalance(deployer.address);
  console.log('Account balance:', ethers.formatEther(balance), 'ETH\n');

  if (balance === 0n) {
    console.error("❌ Deployer has no ETH! Get testnet ETH from https://sepoliafaucet.com/");
    process.exit(1);
  }

  // Load contract artifacts
  const evidenceRegistryArtifact = JSON.parse(
    fs.readFileSync(path.join(__dirname, '../artifacts/contracts/EvidenceRegistry.sol/EvidenceRegistry.json'), 'utf8')
  );
  const subjectAttributeRegistryArtifact = JSON.parse(
    fs.readFileSync(path.join(__dirname, '../artifacts/contracts/SubjectAttributeRegistry.sol/SubjectAttributeRegistry.json'), 'utf8')
  );
  const accessPolicyManagerArtifact = JSON.parse(
    fs.readFileSync(path.join(__dirname, '../artifacts/contracts/AccessPolicyManager.sol/AccessPolicyManager.json'), 'utf8')
  );
  const accessAuditLogArtifact = JSON.parse(
    fs.readFileSync(path.join(__dirname, '../artifacts/contracts/AccessAuditLog.sol/AccessAuditLog.json'), 'utf8')
  );

  console.log("Deploying contracts to Sepolia...\n");

  // 1. Deploy EvidenceRegistry
  console.log("1. Deploying EvidenceRegistry...");
  const EvidenceRegistryFactory = new ethers.ContractFactory(
    evidenceRegistryArtifact.abi,
    evidenceRegistryArtifact.bytecode,
    deployer
  );
  const evidenceRegistry = await EvidenceRegistryFactory.deploy();
  await evidenceRegistry.waitForDeployment();
  const evidenceRegistryAddress = await evidenceRegistry.getAddress();
  console.log(`   ✓ EvidenceRegistry deployed to: ${evidenceRegistryAddress}`);

  // 2. Deploy SubjectAttributeRegistry
  console.log("2. Deploying SubjectAttributeRegistry...");
  const SubjectAttributeRegistryFactory = new ethers.ContractFactory(
    subjectAttributeRegistryArtifact.abi,
    subjectAttributeRegistryArtifact.bytecode,
    deployer
  );
  const subjectAttributeRegistry = await SubjectAttributeRegistryFactory.deploy();
  await subjectAttributeRegistry.waitForDeployment();
  const subjectAttributeRegistryAddress = await subjectAttributeRegistry.getAddress();
  console.log(`   ✓ SubjectAttributeRegistry deployed to: ${subjectAttributeRegistryAddress}`);

  // 3. Deploy AccessPolicyManager
  console.log("3. Deploying AccessPolicyManager...");
  const AccessPolicyManagerFactory = new ethers.ContractFactory(
    accessPolicyManagerArtifact.abi,
    accessPolicyManagerArtifact.bytecode,
    deployer
  );
  const accessPolicyManager = await AccessPolicyManagerFactory.deploy(
    subjectAttributeRegistryAddress,
    evidenceRegistryAddress
  );
  await accessPolicyManager.waitForDeployment();
  const accessPolicyManagerAddress = await accessPolicyManager.getAddress();
  console.log(`   ✓ AccessPolicyManager deployed to: ${accessPolicyManagerAddress}`);

  // 4. Deploy AccessAuditLog
  console.log("4. Deploying AccessAuditLog...");
  const AccessAuditLogFactory = new ethers.ContractFactory(
    accessAuditLogArtifact.abi,
    accessAuditLogArtifact.bytecode,
    deployer
  );
  const accessAuditLog = await AccessAuditLogFactory.deploy();
  await accessAuditLog.waitForDeployment();
  const accessAuditLogAddress = await accessAuditLog.getAddress();
  console.log(`   ✓ AccessAuditLog deployed to: ${accessAuditLogAddress}\n`);

  // Save deployment info
  const deploymentInfo = {
    network: "sepolia",
    chainId: 11155111,
    timestamp: Date.now(),
    deployer: deployer.address,
    contracts: {
      EvidenceRegistry: evidenceRegistryAddress,
      SubjectAttributeRegistry: subjectAttributeRegistryAddress,
      AccessPolicyManager: accessPolicyManagerAddress,
      AccessAuditLog: accessAuditLogAddress
    }
  };

  const deploymentsDir = path.join(__dirname, '../deployments');
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  const deploymentFile = path.join(deploymentsDir, `deployment-sepolia-${Date.now()}.json`);
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));

  console.log("=".repeat(80));
  console.log("DEPLOYMENT COMPLETE!");
  console.log("=".repeat(80));
  console.log("\nContract Addresses:");
  console.log(`EvidenceRegistry:            ${evidenceRegistryAddress}`);
  console.log(`SubjectAttributeRegistry:    ${subjectAttributeRegistryAddress}`);
  console.log(`AccessPolicyManager:         ${accessPolicyManagerAddress}`);
  console.log(`AccessAuditLog:              ${accessAuditLogAddress}`);
  console.log(`\nDeployment info saved to: ${deploymentFile}`);
  
  console.log("\n" + "=".repeat(80));
  console.log("NEXT STEPS:");
  console.log("=".repeat(80));
  console.log("\n1. Update claimguard-peg/.env with these addresses:");
  console.log(`   EVIDENCE_REGISTRY_ADDRESS=${evidenceRegistryAddress}`);
  console.log(`   SUBJECT_ATTRIBUTE_REGISTRY_ADDRESS=${subjectAttributeRegistryAddress}`);
  console.log(`   ACCESS_POLICY_MANAGER_ADDRESS=${accessPolicyManagerAddress}`);
  console.log(`   ACCESS_AUDIT_LOG_ADDRESS=${accessAuditLogAddress}`);
  console.log(`   RPC_URL=${sepoliaRpcUrl}`);
  console.log(`   CHAIN_ID=11155111`);
  console.log("\n2. Restart PEG gateway to connect to Sepolia");
  console.log("\n3. Run E2 tests: python e2_run.py --base-url http://localhost:4000/api\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
