import express from "express";
import bodyParser from "body-parser";
import { config, validateConfig } from "./config";
import { createProvider } from "./blockchain";
import { accessRouter } from "./routes/access";
import { policyRouter } from "./routes/policy";

async function main() {
  validateConfig();

  const app = express();
  app.use(bodyParser.json());

  const provider = createProvider();

  app.get("/health", (_req, res) => {
    res.json({ status: "ok" });
  });

  app.use("/api", accessRouter(provider));
  app.use("/api", policyRouter(provider));

  app.listen(config.port, () => {
    console.log(`ClaimGuard PEG listening on port ${config.port}`);
  });
}

main().catch((err) => {
  console.error("Failed to start PEG:", err);
  process.exit(1);
});
