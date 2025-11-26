import { buildModule } from '@nomicfoundation/hardhat-ignition/modules';

export default buildModule('ClaimguardModule', (m) => {
  const evidenceRegistry = m.contract('EvidenceRegistry');
  const subjectAttributeRegistry = m.contract('SubjectAttributeRegistry');

  const accessPolicyManager = m.contract('AccessPolicyManager', [
    subjectAttributeRegistry,
    evidenceRegistry,
  ]);

  return { evidenceRegistry, subjectAttributeRegistry, accessPolicyManager };
});
