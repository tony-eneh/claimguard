/**
 * File Server
 * Validates tokens before serving evidence.
 * Simulates cloud/IPFS storage layer that enforces token-based access.
 * 
 * Runs on port 5000 by default.
 * Shares in-memory capability store with gateway (single-process setup).
 */

import express, { Request, Response } from "express";
import bodyParser from "body-parser";
import { getCapability } from "./capabilityStore";
import { config } from "./config";
import { Action } from "./types";
import * as fs from "fs";
import * as path from "path";

interface AccessLog {
  timestamp: string;
  token: string;
  resourceId: string;
  action: string;
  subject: string;
  authorized: boolean;
  reason: string;
}

const accessLogs: AccessLog[] = [];

export function createFileServer() {
  const app = express();
  app.use(bodyParser.json());

  // Health check
  app.get("/health", (_req, res) => {
    res.json({ status: "ok" });
  });

  /**
   * POST /fetch
   * Validate token and return evidence metadata (or error).
   * 
   * Request body:
   *  - token: capability token
   *  - resourceId: resource ID (as string)
   *  - action: action type (READ, etc.)
   */
  app.post("/fetch", (req: Request, res: Response) => {
    const { token, resourceId, action } = req.body;

    if (!token || !resourceId || !action) {
      const log: AccessLog = {
        timestamp: new Date().toISOString(),
        token: token || "MISSING",
        resourceId: resourceId?.toString() || "MISSING",
        action: action || "MISSING",
        subject: "UNKNOWN",
        authorized: false,
        reason: "Missing token, resourceId, or action"
      };
      accessLogs.push(log);
      return res.status(400).json({ error: "Missing token, resourceId, or action" });
    }

    // Retrieve capability
    const cap = getCapability(token);

    if (!cap) {
      const log: AccessLog = {
        timestamp: new Date().toISOString(),
        token,
        resourceId: resourceId.toString(),
        action,
        subject: "UNKNOWN",
        authorized: false,
        reason: "Token not found, expired, or invalid"
      };
      accessLogs.push(log);
      return res.status(401).json({ error: "Token not found, expired, or invalid" });
    }

    // Verify resourceId matches
    if (cap.resourceId.toString() !== resourceId.toString()) {
      const log: AccessLog = {
        timestamp: new Date().toISOString(),
        token,
        resourceId: resourceId.toString(),
        action,
        subject: cap.subject,
        authorized: false,
        reason: `Resource mismatch: token bound to ${cap.resourceId.toString()}, requested ${resourceId.toString()}`
      };
      accessLogs.push(log);
      return res.status(403).json({ error: "Token not bound to this resource" });
    }

    // Verify action matches
    const actionNum = Action[action as keyof typeof Action];
    if (actionNum === undefined || cap.action !== actionNum) {
      const log: AccessLog = {
        timestamp: new Date().toISOString(),
        token,
        resourceId: resourceId.toString(),
        action,
        subject: cap.subject,
        authorized: false,
        reason: `Action mismatch: token bound to ${Action[cap.action]}, requested ${action}`
      };
      accessLogs.push(log);
      return res.status(403).json({ error: "Token not bound to this action" });
    }

    // Verify expiry
    if (cap.expiresAt.getTime() < Date.now()) {
      const log: AccessLog = {
        timestamp: new Date().toISOString(),
        token,
        resourceId: resourceId.toString(),
        action,
        subject: cap.subject,
        authorized: false,
        reason: "Token expired"
      };
      accessLogs.push(log);
      return res.status(401).json({ error: "Token expired" });
    }

    // SUCCESS: return evidence metadata
    const log: AccessLog = {
      timestamp: new Date().toISOString(),
      token,
      resourceId: resourceId.toString(),
      action,
      subject: cap.subject,
      authorized: true,
      reason: "OK"
    };
    accessLogs.push(log);

    return res.json({
      authorized: true,
      uri: cap.uri,
      contentHash: cap.contentHash,
      subject: cap.subject,
      expiresAt: cap.expiresAt.toISOString()
    });
  });

  /**
   * GET /logs
   * Return all access logs (for E3 analysis).
   */
  app.get("/logs", (_req, res: Response) => {
    return res.json({ logs: accessLogs, count: accessLogs.length });
  });

  /**
   * POST /logs/clear
   * Clear logs for fresh E3 test run.
   */
  app.post("/logs/clear", (_req: Request, res: Response) => {
    const count = accessLogs.length;
    accessLogs.length = 0;
    return res.json({ cleared: count });
  });

  /**
   * POST /logs/save
   * Save logs to file (for persistence across runs).
   * Request body:
   *  - filename: filename to save to (under experiment_results/e3)
   */
  app.post("/logs/save", (req: Request, res: Response) => {
    const { filename } = req.body;
    if (!filename) {
      return res.status(400).json({ error: "filename required" });
    }

    const dir = path.join(__dirname, "..", "experiment_results", "e3");
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    const filepath = path.join(dir, filename);
    fs.writeFileSync(filepath, JSON.stringify(accessLogs, null, 2));
    return res.json({ saved: filepath, count: accessLogs.length });
  });

  return app;
}

export function startFileServer(port: number = 5000) {
  const app = createFileServer();
  app.listen(port, () => {
    console.log(`File Server listening on port ${port}`);
  });
}
