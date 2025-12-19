import express from "express";
import bodyParser from "body-parser";
import { config, validateConfig } from "./config";
import { createProvider } from "./blockchain";
import { accessRouter } from "./routes/access";
import { policyRouter } from "./routes/policy";
import { rbacAccessRouter } from "./routes/rbac";
import { hybridAccessRouter } from "./routes/hybrid";

async function main() {
  validateConfig();

  const app = express();
  app.use(bodyParser.json());

  const provider = createProvider();

  app.get("/health", (_req, res) => {
    res.json({ status: "ok" });
  });

  // claimguard-peg RBAC routes
  app.use("/api", accessRouter(provider));
  app.use("/api", policyRouter());

  // RBAC policy store and access routes
  app.use("/api", rbacAccessRouter());

  // hybrid rbac+ on-chain logs routes
  app.use("/api", hybridAccessRouter(provider));

  app.listen(config.port, () => {
    console.log(`ClaimGuard PEG listening on port ${config.port}`);
  });
}

