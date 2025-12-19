// src/routes/rbacAccess.ts
import express, { Request, Response } from "express";
import path from "node:path";
import { v4 as uuidv4 } from "uuid";
import { config } from "../config";
import { saveCapability } from "../capabilityStore";
import { Action, AccessRequestBody, Capability } from "../types";
import { RbacStore, SubjectJson, ResourceJson, RbacRule } from "../rbac/store";
import { buildStoresFromOutputs } from "../rbac/load";

const SUBJECTS_JSON = path.resolve(process.cwd(), "outputs", "subjects.json");
const RESOURCES_JSON = path.resolve(process.cwd(), "outputs", "resources.json");

// Map your Action enum to RBAC action strings (keep identical to what generator sends)
function normalizeActionKey(action: string) {
    const key = action as keyof typeof Action;
    if (!(key in Action)) return null;
    return { key, actionEnum: Action[key] };
}

export function rbacAccessRouter() {
    const router = express.Router();

    const store = new RbacStore();
    buildStoresFromOutputs({ store, subjectsPath: SUBJECTS_JSON, resourcesPath: RESOURCES_JSON });

    // Seed baseline RBAC rules to mirror the ABAC policies seeded on-chain
    seedBaselineRules(store);

    // Optional: in-memory RBAC policy rule injection (baseline)
    router.post("/rbac/policy", (req: Request, res: Response) => {
        const body = req.body ?? {};
        const rule: RbacRule = {
            role: body.role,
            action: body.action,
            rType: body.rType,
            caseId: body.caseId,
            allow: Boolean(body.allow),
            maxSensitivity: body.maxSensitivity,
            notBefore: body.notBefore,
            notAfter: body.notAfter,
        };

        if (!rule.role || !rule.action) {
            return res.status(400).json({ error: "role and action are required" });
        }

        store.rules.push(rule);
        return res.json({ ok: true, ruleCount: store.rules.length, rule });
    });

    // Optional reload
    router.post("/rbac/reload", (_req: Request, res: Response) => {
        const counts = buildStoresFromOutputs({
            store,
            subjectsPath: SUBJECTS_JSON,
            resourcesPath: RESOURCES_JSON,
        });
        return res.json({ ok: true, ...counts });
    });

    // POST /rbac/access (same shape as ClaimGuard /access)
    router.post("/rbac/access", async (req: Request, res: Response) => {
        const body = req.body as Partial<AccessRequestBody>;

        if (!body.subject || body.resourceId === undefined || !body.action) {
            return res.status(400).json({ error: "subject, resourceId and action are required" });
        }

        const subject = body.subject as `0x${string}`;

        // Your ClaimGuard casts to BigInt; we’ll accept string/number and then normalize to number for store lookup
        const resourceIdBig = BigInt(body.resourceId as any);
        const resourceIdNum = Number(resourceIdBig); // ok because your dataset ids are small ints

        const actionNorm = normalizeActionKey(String(body.action));
        if (!actionNorm) {
            return res.status(400).json({ error: `Invalid action ${body.action}` });
        }

        try {
            // RBAC decision (cloud-only)
            const decision = store.evaluate({
                subjectAddr: subject,
                resourceId: resourceIdNum,
                action: actionNorm.key, // rules store action as string keys like "READ"
            });

            if (!decision.allow) {
                return res.status(403).json({
                    allowed: false,
                    reason: "Access denied by RBAC policy",
                });
            }

            // Fetch resource metadata from seeded store (to return uri + contentHash)
            const resource = store.resources.get(resourceIdNum);
            if (!resource) {
                return res.status(404).json({ error: "Resource not found" });
            }

            const contentHash = resource.contentHash;
            const uri = resource.uri;

            // Issue capability token (same as ClaimGuard)
            const token = uuidv4();
            const expiresAt = new Date(Date.now() + config.capabilityTtlSeconds * 1000);

            const capability: Capability = {
                token,
                subject,
                resourceId: resourceIdBig,
                action: actionNorm.actionEnum, // keep identical to ClaimGuard Capability type
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
            console.error("Error in /rbac/access:", err);
            return res.status(500).json({ error: "Internal error", details: String(err.message || err) });
        }
    });

    return router;
}

function seedBaselineRules(store: RbacStore) {
    const now = Math.floor(Date.now() / 1000);
    const oneMonth = 30 * 24 * 60 * 60;

    const rules: RbacRule[] = [
        // Insurers: READ any type, sensitivity <= 5
        { role: "INSURER", action: "READ", allow: true, maxSensitivity: 5 },

        // Adjusters: READ/APPEND/UPDATE, sensitivity <= 4
        { role: "ADJUSTER", action: "READ", allow: true, maxSensitivity: 4 },
        { role: "ADJUSTER", action: "APPEND", allow: true, maxSensitivity: 4 },
        { role: "ADJUSTER", action: "UPDATE", allow: true, maxSensitivity: 4 },

        // Police: READ VIDEO + IMAGE, sensitivity <= 3, time-bounded
        { role: "POLICE", action: "READ", rType: "VIDEO", allow: true, maxSensitivity: 3, notBefore: now, notAfter: now + oneMonth },
        { role: "POLICE", action: "READ", rType: "IMAGE", allow: true, maxSensitivity: 3, notBefore: now, notAfter: now + oneMonth },

        // Court: READ any, sensitivity <= 5
        { role: "COURT", action: "READ", allow: true, maxSensitivity: 5 },

        // Garage: READ IMAGE + REPAIR_ESTIMATE, sensitivity <= 2
        { role: "GARAGE", action: "READ", rType: "IMAGE", allow: true, maxSensitivity: 2 },
        { role: "GARAGE", action: "READ", rType: "REPAIR_ESTIMATE", allow: true, maxSensitivity: 2 },

        // Regulator: READ any, max sensitivity
        { role: "REGULATOR", action: "READ", allow: true, maxSensitivity: 5 },
    ];

    store.rules.push(...rules);
}
