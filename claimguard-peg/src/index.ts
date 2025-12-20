import express from "express";
import bodyParser from "body-parser";
import { config, validateConfig } from "./config";
import { createProvider } from "./blockchain";
import { accessRouter } from "./routes/access";
import { rbacAccessRouter } from "./routes/rbac";
import { hybridAccessRouter } from "./routes/hybrid";
import { createFileServer } from "./fileServer";
import type { Server } from "http";

async function main() {
  console.log(`[STARTUP] Validating config...`);
  validateConfig();
  console.log(`[STARTUP] Config validated, mode=${config.mode}, rpc=${config.rpcUrl}`);

  const app = express();
  app.use(bodyParser.json());

  app.get("/health", (_req, res) => {
    res.json({ status: "ok" });
  });

  // Mount based on mode
  if (config.mode === "claimguard") {
    console.log(`[STARTUP] Creating provider for claimguard mode...`);
    const provider = createProvider();
    console.log(`[STARTUP] Provider created, loading routes...`);
    const { policyRouter } = await import("./routes/policy");
    const { measureRouter } = await import("./routes/measure");
    console.log(`[STARTUP] Routes loaded, mounting...`);
    app.use("/api", accessRouter(provider));
    app.use("/api", policyRouter());
    app.use("/api", measureRouter());
    console.log(`[STARTUP] Routes mounted`);
  }

  if (config.mode === "rbac") {
    app.use("/api", rbacAccessRouter());
  }

  if (config.mode === "hybrid") {
    const provider = createProvider();
    app.use("/api", hybridAccessRouter(provider));
  }

  // Start gateway on primary port
  console.log(`[STARTUP] Starting server on port ${config.port}...`);
  const server: Server = app.listen(config.port, () => {
    console.log(`✓ ClaimGuard PEG (${config.mode}) listening on port ${config.port}`);
  });

  // Handle server errors
  server.on("error", (err: Error) => {
    console.error(`[ERROR] Server error:`, err);
  });

  server.on("clientError", (err: Error) => {
    console.error(`[ERROR] Client error:`, err);
  });

  // Set timeout for unresponsive requests
  server.setTimeout(30000);

  // Defer file server startup to next event loop iteration
  setImmediate(() => {
    try {
      console.log(`[STARTUP] Starting file server...`);
      const fileServer = createFileServer();
      const fileServerInstance = fileServer.listen(5000, () => {
        console.log(`✓ File Server listening on port 5000`);
      });
      
      fileServerInstance.on("error", (err: Error) => {
        console.error(`[ERROR] File server error:`, err);
      });
    } catch (err) {
      console.error(`[ERROR] Failed to start file server:`, err);
    }
  });
}

main().catch((err) => {
  console.error("PEG failed to start:", err);
  process.exit(1);
});

