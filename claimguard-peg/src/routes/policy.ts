import express, { Request, Response } from "express";
import { ethers } from "ethers";
import { createSigner, getContracts } from "../blockchain";

/**
 * Body format (all fields required):
 * {
 *   "role": number,
 *   "orgId": string,        // bytes32 hex, or "0x0" for wildcard
 *   "jurisdiction": string, // bytes32 hex, or "0x0"
 *   "rType": number,
 *   "caseId": string,       // bytes32 hex, or "0x0"
 *   "action": number,
 *   "maxSensitivity": number,
 *   "notBefore": number,    // uint64 unix timestamp, 0 for "any"
 *   "notAfter": number,     // uint64 unix timestamp, 0 for "any"
 *   "allow": boolean
 * }
 */
export function policyRouter(provider: ethers.JsonRpcProvider) {
  const router = express.Router();
  const signer = createSigner(provider);
  const { apm } = getContracts(signer);

  router.post("/policy", async (req: Request, res: Response) => {
    try {
      const {
        role,
        orgId,
        jurisdiction,
        rType,
        caseId,
        action,
        maxSensitivity,
        notBefore,
        notAfter,
        allow
      } = req.body ?? {};

      if (
        role === undefined ||
        rType === undefined ||
        action === undefined ||
        maxSensitivity === undefined ||
        orgId === undefined ||
        jurisdiction === undefined ||
        caseId === undefined ||
        allow === undefined
      ) {
        return res.status(400).json({ error: "Missing required fields" });
      }

      const roleNum = Number(role);
      const rTypeNum = Number(rType);
      const actionNum = Number(action);
      const maxSensNum = Number(maxSensitivity);
      const nbNum = Number(notBefore || 0);
      const naNum = Number(notAfter || 0);

      const orgIdBytes = orgId === "0x0" ? ethers.ZeroHash : orgId;
      const jurBytes = jurisdiction === "0x0" ? ethers.ZeroHash : jurisdiction;
      const caseIdBytes = caseId === "0x0" ? ethers.ZeroHash : caseId;

      const start = Date.now();

      const tx = await apm.createPolicy(
        roleNum,
        orgIdBytes,
        jurBytes,
        rTypeNum,
        caseIdBytes,
        actionNum,
        maxSensNum,
        nbNum,
        naNum,
        Boolean(allow)
      );
      const receipt = await tx.wait();

      const end = Date.now();

      return res.json({
        txHash: receipt?.hash,
        blockNumber: receipt?.blockNumber,
        gasUsed: receipt?.gasUsed?.toString(),
        latencyMs: end - start
      });
    } catch (err: any) {
      console.error("Error in /policy:", err);
      return res.status(500).json({
        error: "Internal error",
        details: String(err.message || err)
      });
    }
  });

  return router;
}
