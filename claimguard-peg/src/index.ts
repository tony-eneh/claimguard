import express from "express";
import bodyParser from "body-parser";
import { config, validateConfig } from "./config";
import { createProvider } from "./blockchain";
import { accessRouter } from "./routes/access";
import { rbacAccessRouter } from "./routes/rbac";
import { hybridAccessRouter } from "./routes/hybrid";

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
    app.use("/api", accessRouter(provider));
    app.use("/api", policyRouter());
  }

  if (config.mode === "rbac") {
    app.use("/api", rbacAccessRouter());
  }

  if (config.mode === "hybrid") {
    const provider = createProvider();
    app.use("/api", hybridAccessRouter(provider));
  }

  app.listen(config.port, () => {
    console.log(`ClaimGuard PEG (${config.mode}) listening on port ${config.port}`);
  });
}

main().catch((err) => {
  console.error("PEG failed to start:", err);
  process.exit(1);
});

