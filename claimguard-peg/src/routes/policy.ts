// src/routes/policy.ts
import express, { Request, Response } from 'express';
import { Hex, decodeEventLog } from 'viem';
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

      // Try to extract policyId from PolicyCreated event
      let policyId: number | undefined = undefined;
      try {
        for (const log of receipt.logs) {
          try {
            const ev: any = decodeEventLog({
              abi: apmAbi as any,
              data: log.data as Hex,
              topics: (log.topics as any),
            }) as any;
            if (ev && ev.eventName === 'PolicyCreated') {
              const args: any = (ev as any).args as any;
              if (args && args.policyId !== undefined) {
                policyId = Number(args.policyId);
                break;
              }
            }
          } catch (_e) {
            // skip non-matching logs
          }
        }
      } catch (_e) {
        // ignore
      }

      const end = Date.now();

      return res.json({
        txHash: hash,
        blockNumber: Number(receipt.blockNumber),
        gasUsed: receipt.gasUsed.toString(),
        policyId,
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

  // GET /policy/count -> { nextPolicyId }
  router.get('/policy/count', async (_req: Request, res: Response) => {
    try {
      const next = (await publicClient.readContract({
        address: apmAddress,
        abi: apmAbi,
        functionName: 'nextPolicyId',
        args: [],
      })) as bigint;
      return res.json({ nextPolicyId: Number(next) });
    } catch (err: any) {
      console.error('Error in /policy/count:', err);
      return res.status(500).json({ error: 'Internal error', details: String(err?.message ?? err) });
    }
  });

  // GET /policy/list?offset=0&limit=200 -> list of policies (active/inactive)
  router.get('/policy/list', async (req: Request, res: Response) => {
    try {
      const offset = Math.max(0, Number(req.query.offset ?? 0));
      const limit = Math.min(1000, Math.max(1, Number(req.query.limit ?? 200)));

      const next = (await publicClient.readContract({
        address: apmAddress,
        abi: apmAbi,
        functionName: 'nextPolicyId',
        args: [],
      })) as bigint;
      const maxId = Number(next) - 1;
      if (maxId <= 0) {
        return res.json({ total: 0, items: [] });
      }

      const start = Math.min(maxId, offset + 1);
      const end = Math.min(maxId, offset + limit);

      const items: any[] = [];
      for (let id = start; id <= end; id++) {
        try {
          const p: any = await publicClient.readContract({
            address: apmAddress,
            abi: apmAbi,
            functionName: 'getPolicy',
            args: [BigInt(id)],
          });
          // p is a tuple matching PolicyRule
          items.push({ id, ...p });
        } catch (_e) {
          // skip
        }
      }

      return res.json({ total: maxId, items });
    } catch (err: any) {
      console.error('Error in /policy/list:', err);
      return res.status(500).json({ error: 'Internal error', details: String(err?.message ?? err) });
    }
  });

  // POST /policy/revoke { policyId }
  router.post('/policy/revoke', async (req: Request, res: Response) => {
    try {
      const { policyId } = req.body ?? {};
      if (policyId === undefined) {
        return res.status(400).json({ error: 'policyId is required' });
      }
      const start = Date.now();
      const hash = await walletClient.writeContract({
        address: apmAddress,
        abi: apmAbi,
        functionName: 'revokePolicy',
        args: [BigInt(policyId)],
      });
      const receipt = await publicClient.waitForTransactionReceipt({ hash });
      const end = Date.now();
      return res.json({ txHash: hash, blockNumber: Number(receipt.blockNumber), gasUsed: receipt.gasUsed.toString(), latencyMs: end - start });
    } catch (err: any) {
      console.error('Error in /policy/revoke:', err);
      return res.status(500).json({ error: 'Internal error', details: String(err?.message ?? err) });
    }
  });

  return router;
}
