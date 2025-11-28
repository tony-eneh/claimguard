"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.accessRouter = accessRouter;
const express_1 = __importDefault(require("express"));
const uuid_1 = require("uuid");
const types_1 = require("../types");
const config_1 = require("../config");
const blockchain_1 = require("../blockchain");
const capabilityStore_1 = require("../capabilityStore");
function accessRouter(provider) {
    const router = express_1.default.Router();
    const { apm, evidenceReg } = (0, blockchain_1.getContracts)(provider);
    // POST /access
    router.post("/access", async (req, res) => {
        const body = req.body;
        if (!body.subject || !body.resourceId || !body.action) {
            return res.status(400).json({ error: "subject, resourceId and action are required" });
        }
        const subject = body.subject;
        const resourceId = BigInt(body.resourceId);
        const actionKey = body.action;
        if (!(actionKey in types_1.Action)) {
            return res.status(400).json({ error: `Invalid action ${body.action}` });
        }
        const actionEnum = types_1.Action[actionKey];
        try {
            const allowed = await apm.checkAccess(subject, resourceId, actionEnum);
            if (!allowed) {
                return res.status(403).json({
                    allowed: false,
                    reason: "Access denied by on-chain policy"
                });
            }
            // Fetch resource metadata for URI + contentHash
            const resource = await evidenceReg.getResource(resourceId);
            const exists = resource[7];
            if (!exists) {
                return res.status(404).json({ error: "Resource not found" });
            }
            const contentHash = resource[1];
            const uri = resource[2];
            // Issue capability token
            const token = (0, uuid_1.v4)();
            const expiresAt = new Date(Date.now() + config_1.config.capabilityTtlSeconds * 1000);
            const capability = {
                token,
                subject,
                resourceId,
                action: actionEnum,
                uri,
                contentHash,
                expiresAt
            };
            (0, capabilityStore_1.saveCapability)(capability);
            return res.json({
                allowed: true,
                capability: {
                    token,
                    expiresAt: capability.expiresAt.toISOString(),
                    uri,
                    contentHash,
                    resourceId: resourceId.toString()
                }
            });
        }
        catch (err) {
            console.error("Error in /access:", err);
            return res.status(500).json({ error: "Internal error", details: String(err.message || err) });
        }
    });
    // Optional: GET /capability/:token (for end-to-end tests)
    // In a real system this would proxy to S3/MinIO/IPFS.
    router.get("/capability/:token", (req, res) => {
        const token = req.params.token;
        const cap = (0, capabilityStore_1.getCapability)(token);
        if (!cap) {
            return res.status(404).json({ error: "Capability not found or expired" });
        }
        // For now we just return metadata; your load-test tool can treat
        // this as the "evidence fetch" step.
        return res.json({
            token: cap.token,
            uri: cap.uri,
            contentHash: cap.contentHash,
            resourceId: cap.resourceId.toString(),
            action: cap.action,
            expiresAt: cap.expiresAt.toISOString()
        });
    });
    return router;
}
