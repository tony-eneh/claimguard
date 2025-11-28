"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.config = void 0;
exports.validateConfig = validateConfig;
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
exports.config = {
    port: Number(process.env.PORT || 4000),
    rpcUrl: process.env.RPC_URL || 'http://127.0.0.1:8545',
    gatewayPrivateKey: process.env.GATEWAY_PRIVATE_KEY || '',
    accessPolicyManagerAddress: process.env.ACCESS_POLICY_MANAGER_ADDRESS || '',
    evidenceRegistryAddress: process.env.EVIDENCE_REGISTRY_ADDRESS || '',
    subjectAttributeRegistryAddress: process.env.SUBJECT_ATTRIBUTE_REGISTRY_ADDRESS || '',
    capabilityTtlSeconds: Number(process.env.CAPABILITY_TTL_SECONDS || 60),
};
function validateConfig() {
    const missing = [];
    if (!exports.config.gatewayPrivateKey)
        missing.push('GATEWAY_PRIVATE_KEY');
    if (!exports.config.accessPolicyManagerAddress)
        missing.push('ACCESS_POLICY_MANAGER_ADDRESS');
    if (!exports.config.evidenceRegistryAddress)
        missing.push('EVIDENCE_REGISTRY_ADDRESS');
    if (!exports.config.subjectAttributeRegistryAddress)
        missing.push('SUBJECT_ATTRIBUTE_REGISTRY_ADDRESS');
    if (missing.length > 0) {
        throw new Error(`Missing required env vars: ${missing.join(', ')}`);
    }
}
