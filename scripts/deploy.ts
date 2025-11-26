import { ethers } from 'ethers';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Helper to wait for a specified time
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

async function main() {
  console.log('Starting deployment...\n');

  // Connect to local Hardhat node
  const provider = new ethers.JsonRpcProvider('http://127.0.0.1:8545');
  
  // Use first default Hardhat account
  const privateKey = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80';
  const deployer = new ethers.Wallet(privateKey, provider);
  
  console.log('Deploying contracts with account:', deployer.address);
  console.log('Account balance:', ethers.formatEther(await provider.getBalance(deployer.address)), 'ETH\n');

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

  // Deploy EvidenceRegistry
  console.log('Deploying EvidenceRegistry...');
  let nonce = await provider.getTransactionCount(deployer.address, 'latest');
  console.log('  Using nonce:', nonce);
  
  const EvidenceRegistry = new ethers.ContractFactory(
    evidenceRegistryArtifact.abi,
    evidenceRegistryArtifact.bytecode,
    deployer
  );
  const evidenceRegistry = await EvidenceRegistry.deploy({ nonce });
  const receipt1 = await evidenceRegistry.deploymentTransaction()?.wait();
  console.log('  Transaction mined in block:', receipt1?.blockNumber);
  const evidenceRegistryAddress = await evidenceRegistry.getAddress();
  console.log('✓ EvidenceRegistry deployed to:', evidenceRegistryAddress);
  
  // Wait a bit to ensure state is updated
  await sleep(500);

  // Deploy SubjectAttributeRegistry
  console.log('\nDeploying SubjectAttributeRegistry...');
  nonce = await provider.getTransactionCount(deployer.address, 'latest');
  console.log('  Using nonce:', nonce);
  
  const SubjectAttributeRegistry = new ethers.ContractFactory(
    subjectAttributeRegistryArtifact.abi,
    subjectAttributeRegistryArtifact.bytecode,
    deployer
  );
  const subjectAttributeRegistry = await SubjectAttributeRegistry.deploy({ nonce });
  const receipt2 = await subjectAttributeRegistry.deploymentTransaction()?.wait();
  console.log('  Transaction mined in block:', receipt2?.blockNumber);
  const subjectAttributeRegistryAddress = await subjectAttributeRegistry.getAddress();
  console.log('✓ SubjectAttributeRegistry deployed to:', subjectAttributeRegistryAddress);
  
  // Wait a bit to ensure state is updated
  await sleep(500);

  // Deploy AccessPolicyManager
  console.log('\nDeploying AccessPolicyManager...');
  nonce = await provider.getTransactionCount(deployer.address, 'latest');
  console.log('  Using nonce:', nonce);
  
  const AccessPolicyManager = new ethers.ContractFactory(
    accessPolicyManagerArtifact.abi,
    accessPolicyManagerArtifact.bytecode,
    deployer
  );
  const accessPolicyManager = await AccessPolicyManager.deploy(
    subjectAttributeRegistryAddress,
    evidenceRegistryAddress,
    { nonce }
  );
  const receipt3 = await accessPolicyManager.deploymentTransaction()?.wait();
  console.log('  Transaction mined in block:', receipt3?.blockNumber);
  const accessPolicyManagerAddress = await accessPolicyManager.getAddress();
  console.log('✓ AccessPolicyManager deployed to:', accessPolicyManagerAddress);

  // Save deployment addresses
  const network = await provider.getNetwork();
  const deploymentInfo = {
    network: network.name,
    chainId: network.chainId.toString(),
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: {
      EvidenceRegistry: evidenceRegistryAddress,
      SubjectAttributeRegistry: subjectAttributeRegistryAddress,
      AccessPolicyManager: accessPolicyManagerAddress,
    },
  };

  const deploymentDir = path.join(__dirname, '../deployments');
  if (!fs.existsSync(deploymentDir)) {
    fs.mkdirSync(deploymentDir, { recursive: true });
  }

  const deploymentFile = path.join(deploymentDir, `deployment-${Date.now()}.json`);
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));

  console.log('\n' + '='.repeat(60));
  console.log('Deployment Summary');
  console.log('='.repeat(60));
  console.log('Network:', deploymentInfo.network);
  console.log('Chain ID:', deploymentInfo.chainId);
  console.log('Deployer:', deployer.address);
  console.log('\nContract Addresses:');
  console.log('  EvidenceRegistry:', evidenceRegistryAddress);
  console.log('  SubjectAttributeRegistry:', subjectAttributeRegistryAddress);
  console.log('  AccessPolicyManager:', accessPolicyManagerAddress);
  console.log('\nDeployment info saved to:', deploymentFile);
  console.log('='.repeat(60));

  // Update .env file suggestion
  console.log('\nUpdate your claimguard-peg/.env file with:');
  console.log(`EVIDENCE_REGISTRY_ADDRESS=${evidenceRegistryAddress}`);
  console.log(`SUBJECT_ATTRIBUTE_REGISTRY_ADDRESS=${subjectAttributeRegistryAddress}`);
  console.log(`ACCESS_POLICY_MANAGER_ADDRESS=${accessPolicyManagerAddress}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
