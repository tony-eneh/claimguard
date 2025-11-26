import express, { Request, Response } from "express";
import { ethers } from "ethers";
import { v4 as uuidv4 } from "uuid";
import { Action, AccessRequestBody, Capability } from "../types";
import { config } from "../config";
import { getContracts } from "../blockchain";
import { saveCapability, getCapability } from "../capabilityStore";

export function accessRouter(provider: ethers.JsonRpcProvider) {
  const router = express.Router();
  const { apm, evidenceReg } = getContracts(provider);

  // POST /access
  router.post("/access", async (req: Request, res: Response) => {
    const body = req.body as Partial<AccessRequestBody>;

    if (!body.subject || !body.resourceId || !body.action) {
      return res.status(400).json({ error: "subject, resourceId and action are required" });
    }

    const subject = body.subject;
    const resourceId = BigInt(body.resourceId);
    const actionKey = body.action as keyof typeof Action;

    if (!(actionKey in Action)) {
      return res.status(400).json({ error: `Invalid action ${body.action}` });
    }

    const actionEnum = Action[actionKey];

    try {
      const allowed: boolean = await apm.checkAccess(subject, resourceId, actionEnum);

      if (!allowed) {
        return res.status(403).json({
          allowed: false,
          reason: "Access denied by on-chain policy"
        });
      }

      // Fetch resource metadata for URI + contentHash
      const resource = await evidenceReg.getResource(resourceId);
      const exists: boolean = resource[7];
      if (!exists) {
        return res.status(404).json({ error: "Resource not found" });
      }

      const contentHash: string = resource[1];
      const uri: string = resource[2];

      // Issue capability token
      const token = uuidv4();
      const expiresAt = new Date(Date.now() + config.capabilityTtlSeconds * 1000);

      const capability: Capability = {
        token,
        subject,
        resourceId,
        action: actionEnum,
        uri,
        contentHash,
        expiresAt
      };

      saveCapability(capability);

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
    } catch (err: any) {
      console.error("Error in /access:", err);
      return res.status(500).json({ error: "Internal error", details: String(err.message || err) });
    }
  });

  // Optional: GET /capability/:token (for end-to-end tests)
  // In a real system this would proxy to S3/MinIO/IPFS.
  router.get("/capability/:token", (req: Request, res: Response) => {
    const token = req.params.token;
    const cap = getCapability(token);
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
