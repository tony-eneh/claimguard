import express from "express";
import bodyParser from "body-parser";
import { config, validateConfig } from "./config";
import { createProvider } from "./blockchain";
import { accessRouter } from "./routes/access";
import { rbacAccessRouter } from "./routes/rbac";
import { hybridAccessRouter } from "./routes/hybrid";
import { createFileServer } from "./fileServer";

async function main() {
  validateConfig();

  const app = express();
  app.use(bodyParser.json());

  app.get("/health", (_req, res) => {
    res.json({ status: "ok" });
  });

  // Mount based on mode
  if (config.mode === "claimguard") {
    const provider = createProvider();
    const { policyRouter } = await import("./routes/policy");
    const { measureRouter } = await import("./routes/measure");
    app.use("/api", accessRouter(provider));
    app.use("/api", policyRouter());
    app.use("/api", measureRouter());
  }

  if (config.mode === "rbac") {
    app.use("/api", rbacAccessRouter());
  }

  if (config.mode === "hybrid") {
    const provider = createProvider();
    app.use("/api", hybridAccessRouter(provider));
  }

  // Start gateway on primary port
  app.listen(config.port, () => {
    console.log(`ClaimGuard PEG (${config.mode}) listening on port ${config.port}`);
  });

  // Optionally start file server on port 5000 (for E3 testing)
  const fileServer = createFileServer();
  fileServer.listen(5000, () => {
    console.log(`File Server listening on port 5000`);
  });
}

main().catch((err) => {
  console.error("PEG failed to start:", err);
  process.exit(1);
});

