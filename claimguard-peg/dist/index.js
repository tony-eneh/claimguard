"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const body_parser_1 = __importDefault(require("body-parser"));
const config_1 = require("./config");
const blockchain_1 = require("./blockchain");
const access_1 = require("./routes/access");
const policy_1 = require("./routes/policy");
async function main() {
    (0, config_1.validateConfig)();
    const app = (0, express_1.default)();
    app.use(body_parser_1.default.json());
    const provider = (0, blockchain_1.createProvider)();
    app.get("/health", (_req, res) => {
        res.json({ status: "ok" });
    });
    app.use("/api", (0, access_1.accessRouter)(provider));
    app.use("/api", (0, policy_1.policyRouter)(provider));
    app.listen(config_1.config.port, () => {
        console.log(`ClaimGuard PEG listening on port ${config_1.config.port}`);
    });
}
main().catch((err) => {
    console.error("Failed to start PEG:", err);
    process.exit(1);
});
