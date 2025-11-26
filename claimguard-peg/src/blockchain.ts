// blockchain.ts
import { ethers } from 'ethers';
import { config } from './config';
import evidenceRegistryArtifact from '../../artifacts/contracts/EvidenceRegistry.sol/EvidenceRegistry.json';
import subjectAttrRegistryArtifact from '../../artifacts/contracts/SubjectAttributeRegistry.sol/SubjectAttributeRegistry.json';
import accessPolicyManagerArtifact from '../../artifacts/contracts/AccessPolicyManager.sol/AccessPolicyManager.json';

const evidenceRegistryAbi = evidenceRegistryArtifact.abi;
const subjectAttrRegistryAbi = subjectAttrRegistryArtifact.abi;
const accessPolicyManagerAbi = accessPolicyManagerArtifact.abi;

export function createProvider() {
  return new ethers.JsonRpcProvider(config.rpcUrl);
}

export function createSigner(provider: ethers.JsonRpcProvider) {
  const wallet = new ethers.Wallet(config.gatewayPrivateKey, provider);
  return wallet;
}

export function getContracts(
  providerOrSigner: ethers.Provider | ethers.Signer
) {
  const apm = new ethers.Contract(
    config.accessPolicyManagerAddress,
    accessPolicyManagerAbi,
    providerOrSigner
  );

  const evidenceReg = new ethers.Contract(
    config.evidenceRegistryAddress,
    evidenceRegistryAbi,
    providerOrSigner
  );

  const subjectReg = new ethers.Contract(
    config.subjectAttributeRegistryAddress,
    subjectAttrRegistryAbi,
    providerOrSigner
  );

  return { apm, evidenceReg, subjectReg };
}
