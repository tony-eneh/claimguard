import express, { Request, Response } from 'express';
import { Hex } from 'viem';
import accessPolicyManagerArtifact from '../../../artifacts/contracts/AccessPolicyManager.sol/AccessPolicyManager.json';
import { publicClient } from '../viemClients';

const apmAbi = accessPolicyManagerArtifact.abi;
const apmAddress = process.env.ACCESS_POLICY_MANAGER_ADDRESS as `0x${string}`;

export function measureRouter() {
  const router = express.Router();

  // POST /measure/check-access { subject, resourceId, action }
  // Returns { allowed, gasEstimate, latencyMs }
  router.post('/measure/check-access', async (req: Request, res: Response) => {
    try {
      const { subject, resourceId, action } = req.body ?? {};
      if (!subject || resourceId === undefined || action === undefined) {
        return res.status(400).json({ error: 'subject, resourceId, action are required' });
      }

      const start = Date.now();
      // Use simulateContract to get gas estimation and call result for view function
      const sim = await publicClient.simulateContract({
        address: apmAddress,
        abi: apmAbi as any,
        functionName: 'checkAccess',
        args: [subject as `0x${string}`, BigInt(resourceId), Number(action)],
        account: subject as `0x${string}`,
      });
      const allowed = Boolean(sim.result as any);
      const gasEstimate = sim.request.gas ? Number(sim.request.gas) : null;
      const end = Date.now();
      return res.json({ allowed, gasEstimate, latencyMs: end - start });
    } catch (err: any) {
      console.error('Error in /measure/check-access:', err);
      return res.status(500).json({ error: 'Internal error', details: String(err?.message ?? err) });
    }
  });

  return router;
}
