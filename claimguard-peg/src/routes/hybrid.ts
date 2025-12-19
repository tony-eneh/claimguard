// src/routes/hybridAccess.ts
import express, { Request, Response } from "express";
import path from "node:path";
import { v4 as uuidv4 } from "uuid";
import { ethers } from "ethers";
import { Action, AccessRequestBody, Capability } from "../types";
import { config } from "../config";
import { saveCapability } from "../capabilityStore";
import { RbacStore } from "../rbac/store";
import { buildStoresFromOutputs } from "../rbac/load";

// You’ll deploy this small contract: AccessAuditLog.sol (emit event)
// and set ACCESS_AUDIT_LOG_ADDRESS
import auditArtifact from "../../../artifacts/contracts/AccessAuditLog.sol/AccessAuditLog.json";

const SUBJECTS_JSON = path.resolve(process.cwd(), "outputs", "subjects.json");
const RESOURCES_JSON = path.resolve(process.cwd(), "outputs", "resources.json");

function normalizeActionKey(action: string) {
    const key = action as keyof typeof Action;
    if (!(key in Action)) return null;
    return { key, actionEnum: Action[key] };
}

export function hybridAccessRouter(provider: ethers.JsonRpcProvider) {
    const router = express.Router();

    const store = new RbacStore();
    buildStoresFromOutputs({ store, subjectsPath: SUBJECTS_JSON, resourcesPath: RESOURCES_JSON });

    const auditAddress = process.env.ACCESS_AUDIT_LOG_ADDRESS;
    if (!auditAddress) {
        console.warn("ACCESS_AUDIT_LOG_ADDRESS not set; /hybrid/access will fail audit logging.");
    }

    const signer = new ethers.Wallet(process.env.DEPLOYER_PRIVATE_KEY as string, provider);
    const audit = new ethers.Contract(auditAddress as string, auditArtifact.abi, signer);

    // POST /hybrid/access (same response shape as ClaimGuard /access)
    router.post("/hybrid/access", async (req: Request, res: Response) => {
        const body = req.body as Partial<AccessRequestBody>;

        if (!body.subject || body.resourceId === undefined || !body.action) {
            return res.status(400).json({ error: "subject, resourceId and action are required" });
        }

        const subject = body.subject as `0x${string}`;
        const resourceIdBig = BigInt(body.resourceId as any);
        const resourceIdNum = Number(resourceIdBig);

        const actionNorm = normalizeActionKey(String(body.action));
        if (!actionNorm) {
            return res.status(400).json({ error: `Invalid action ${body.action}` });
        }

        try {
            // 1) RBAC decision
            const decision = store.evaluate({
                subjectAddr: subject,
                resourceId: resourceIdNum,
                action: actionNorm.key,
            });

            // 2) Audit log on-chain (allow + deny)
            // Log resourceId + action as hashes to keep event fixed-size
            const ridHash = ethers.keccak256(ethers.toUtf8Bytes(resourceIdBig.toString()));
            const actHash = ethers.keccak256(ethers.toUtf8Bytes(actionNorm.key));

            try {
                // fire-and-forget (fast). If you want “audit latency”, await tx.wait()
                const tx = await audit.logAccess(subject, ridHash, actHash, decision.allow);
                // optionally: await tx.wait();
            } catch (auditErr: any) {
                // For baseline fairness, don’t block decision on audit failures; just surface it
                console.warn("Audit log failed:", auditErr?.message || auditErr);
            }

            if (!decision.allow) {
                return res.status(403).json({
                    allowed: false,
                    reason: "Access denied by RBAC policy",
                });
            }

            // 3) Fetch resource metadata
            const resource = store.resources.get(resourceIdNum);
            if (!resource) {
                return res.status(404).json({ error: "Resource not found" });
            }

            const contentHash = resource.contentHash;
            const uri = resource.uri;

            // 4) Capability issuance (identical to ClaimGuard)
            const token = uuidv4();
            const expiresAt = new Date(Date.now() + config.capabilityTtlSeconds * 1000);

            const capability: Capability = {
                token,
                subject,
                resourceId: resourceIdBig,
                action: actionNorm.actionEnum,
                uri,
                contentHash,
                expiresAt,
            };

            saveCapability(capability);

            return res.json({
                allowed: true,
                capability: {
                    token,
                    expiresAt: capability.expiresAt.toISOString(),
                    uri,
                    contentHash,
                    resourceId: resourceIdBig.toString(),
                },
            });
        } catch (err: any) {
            console.error("Error in /hybrid/access:", err);
            return res.status(500).json({ error: "Internal error", details: String(err.message || err) });
        }
    });

    return router;
}
