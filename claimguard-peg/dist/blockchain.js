"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createProvider = createProvider;
exports.createSigner = createSigner;
exports.getContracts = getContracts;
// blockchain.ts
const ethers_1 = require("ethers");
const config_1 = require("./config");
const EvidenceRegistry_json_1 = __importDefault(require("../../artifacts/contracts/EvidenceRegistry.sol/EvidenceRegistry.json"));
const SubjectAttributeRegistry_json_1 = __importDefault(require("../../artifacts/contracts/SubjectAttributeRegistry.sol/SubjectAttributeRegistry.json"));
const AccessPolicyManager_json_1 = __importDefault(require("../../artifacts/contracts/AccessPolicyManager.sol/AccessPolicyManager.json"));
const evidenceRegistryAbi = EvidenceRegistry_json_1.default.abi;
const subjectAttrRegistryAbi = SubjectAttributeRegistry_json_1.default.abi;
const accessPolicyManagerAbi = AccessPolicyManager_json_1.default.abi;
function createProvider() {
    return new ethers_1.ethers.JsonRpcProvider(config_1.config.rpcUrl);
}
function createSigner(provider) {
    const wallet = new ethers_1.ethers.Wallet(config_1.config.gatewayPrivateKey, provider);
    return wallet;
}
function getContracts(providerOrSigner) {
    const apm = new ethers_1.ethers.Contract(config_1.config.accessPolicyManagerAddress, accessPolicyManagerAbi, providerOrSigner);
    const evidenceReg = new ethers_1.ethers.Contract(config_1.config.evidenceRegistryAddress, evidenceRegistryAbi, providerOrSigner);
    const subjectReg = new ethers_1.ethers.Contract(config_1.config.subjectAttributeRegistryAddress, subjectAttrRegistryAbi, providerOrSigner);
    return { apm, evidenceReg, subjectReg };
}
