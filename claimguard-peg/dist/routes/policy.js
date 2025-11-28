"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.policyRouter = policyRouter;
const express_1 = __importDefault(require("express"));
const ethers_1 = require("ethers");
const blockchain_1 = require("../blockchain");
const config_1 = require("../config");
function policyRouter(provider) {
    const router = express_1.default.Router();
    router.post("/policy", async (req, res) => {
        try {
            const { role, orgId, jurisdiction, rType, caseId, action, maxSensitivity, notBefore, notAfter, allow } = req.body ?? {};
            if (role === undefined ||
                rType === undefined ||
                action === undefined ||
                maxSensitivity === undefined ||
                orgId === undefined ||
                jurisdiction === undefined ||
                caseId === undefined ||
                allow === undefined) {
                return res.status(400).json({ error: "Missing required fields" });
            }
            const roleNum = Number(role);
            const rTypeNum = Number(rType);
            const actionNum = Number(action);
            const maxSensNum = Number(maxSensitivity);
            const nbNum = Number(notBefore || 0);
            const naNum = Number(notAfter || 0);
            const orgIdBytes = orgId === "0x0" ? ethers_1.ethers.ZeroHash : orgId;
            const jurBytes = jurisdiction === "0x0" ? ethers_1.ethers.ZeroHash : jurisdiction;
            const caseIdBytes = caseId === "0x0" ? ethers_1.ethers.ZeroHash : caseId;
            // ⚠️ IMPORTANT: create a fresh signer per request to avoid nonce cache issues
            const signer = new ethers_1.ethers.Wallet(config_1.config.gatewayPrivateKey, provider);
            const { apm } = (0, blockchain_1.getContracts)(signer);
            const start = Date.now();
            const tx = await apm.createPolicy(roleNum, orgIdBytes, jurBytes, rTypeNum, caseIdBytes, actionNum, maxSensNum, nbNum, naNum, Boolean(allow));
            const receipt = await tx.wait(); // waits for confirmation
            const end = Date.now();
            return res.json({
                txHash: receipt?.hash,
                blockNumber: receipt?.blockNumber,
                gasUsed: receipt?.gasUsed?.toString(),
                latencyMs: end - start
            });
        }
        catch (err) {
            console.error("Error in /policy:", err);
            return res.status(500).json({
                error: "Internal error",
                details: String(err.message || err)
            });
        }
    });
    return router;
}
