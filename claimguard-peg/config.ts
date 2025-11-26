// config.ts
export const config = {
  port: Number(process.env.PORT || 4000),
  rpcUrl: process.env.RPC_URL || "http://127.0.0.1:8545",
  gatewayPrivateKey: process.env.GATEWAY_PRIVATE_KEY || "",
  accessPolicyManagerAddress: process.env.ACCESS_POLICY_MANAGER_ADDRESS || "",
  evidenceRegistryAddress: process.env.EVIDENCE_REGISTRY_ADDRESS || "",
  subjectAttributeRegistryAddress: process.env.SUBJECT_ATTRIBUTE_REGISTRY_ADDRESS || "",
  capabilityTtlSeconds: Number(process.env.CAPABILITY_TTL_SECONDS || 60)
};

export function validateConfig() {
  const missing: string[] = [];
  if (!config.gatewayPrivateKey) missing.push("GATEWAY_PRIVATE_KEY");
  if (!config.accessPolicyManagerAddress) missing.push("ACCESS_POLICY_MANAGER_ADDRESS");
  if (!config.evidenceRegistryAddress) missing.push("EVIDENCE_REGISTRY_ADDRESS");
  if (!config.subjectAttributeRegistryAddress) missing.push("SUBJECT_ATTRIBUTE_REGISTRY_ADDRESS");

  if (missing.length > 0) {
    throw new Error(`Missing required env vars: ${missing.join(", ")}`);
  }
}
