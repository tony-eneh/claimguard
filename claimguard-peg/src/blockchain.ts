// blockchain.ts
import { ethers } from 'ethers';
import { config } from './config';

const accessPolicyManagerAbi = [
  'function checkAccess(address subject, uint256 resourceId, uint8 action) public view returns (bool)',
  'function createPolicy(uint8 role, bytes32 orgId, bytes32 jurisdiction, uint8 rType, bytes32 caseId, uint8 action, uint8 maxSensitivity, uint64 notBefore, uint64 notAfter, bool allow) external returns (uint256)',
];

const evidenceRegistryAbi = [
  'function getResource(uint256 resourceId) external view returns ( \
        uint256 id, \
        bytes32 contentHash, \
        string uri, \
        bytes32 caseId, \
        uint8 rType, \
        uint8 sensitivity, \
        address owner, \
        bool exists \
   )',
  'function registerResource(bytes32 contentHash, string calldata uri, bytes32 caseId, uint8 rType, uint8 sensitivity) external returns (uint256 resourceId)',
];

const subjectAttrRegistryAbi = [
  'function setSubjectAttributes(address subject, uint8 role, bytes32 orgId, bytes32 jurisdiction, bool isActive) external',
];

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
