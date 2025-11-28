// src/routes/policy.ts
import express, { Request, Response } from 'express';
import { Hex } from 'viem';
import { publicClient, walletClient } from '../viemClients';
import accessPolicyManagerArtifact from '../../../artifacts/contracts/AccessPolicyManager.sol/AccessPolicyManager.json';
const apmAbi = accessPolicyManagerArtifact.abi;

const apmAddress = process.env.ACCESS_POLICY_MANAGER_ADDRESS as `0x${string}`;

export function policyRouter() {
  const router = express.Router();

  router.post('/policy', async (req: Request, res: Response) => {
    try {
      const body = req.body ?? {};
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
        allow,
      } = body;

      // Basic validation
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
        return res.status(400).json({
          error:
            'Missing required fields (role, orgId, jurisdiction, rType, caseId, action, maxSensitivity, allow)',
        });
      }

      const roleNum = Number(role);
      const rTypeNum = Number(rType);
      const actionNum = Number(action);
      const maxSensNum = Number(maxSensitivity);
      const nbNum = Number(notBefore ?? 0);
      const naNum = Number(notAfter ?? 0);

      const orgIdBytes: Hex =
        orgId === '0x0' || orgId === '' || orgId === null
          ? (('0x' + '0'.repeat(64)) as Hex)
          : (orgId as Hex);

      const jurBytes: Hex =
        jurisdiction === '0x0' || jurisdiction === '' || jurisdiction === null
          ? (('0x' + '0'.repeat(64)) as Hex)
          : (jurisdiction as Hex);

      const caseIdBytes: Hex =
        caseId === '0x0' || caseId === '' || caseId === null
          ? (('0x' + '0'.repeat(64)) as Hex)
          : (caseId as Hex);

      const start = Date.now();

      // Send tx via viem – this handles nonce correctly
      const hash = await walletClient.writeContract({
        address: apmAddress,
        abi: apmAbi,
        functionName: 'createPolicy', // or addOrUpdatePolicy if that's your fn
        args: [
          roleNum,
          orgIdBytes,
          jurBytes,
          rTypeNum,
          caseIdBytes,
          actionNum,
          maxSensNum,
          BigInt(nbNum),
          BigInt(naNum),
          Boolean(allow),
        ],
      });

      const receipt = await publicClient.waitForTransactionReceipt({ hash });

      const end = Date.now();

      return res.json({
        txHash: hash,
        blockNumber: Number(receipt.blockNumber),
        gasUsed: receipt.gasUsed.toString(),
        latencyMs: end - start,
      });
    } catch (err: any) {
      console.error('Error in /policy:', err);
      return res.status(500).json({
        error: 'Internal error',
        details: String(err?.message ?? err),
      });
    }
  });

  return router;
}
