"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const body_parser_1 = __importDefault(require("body-parser"));
const config_1 = require("./config");
const blockchain_1 = require("./blockchain");
const access_1 = require("./routes/access");
const rbac_1 = require("./routes/rbac");
const hybrid_1 = require("./routes/hybrid");
const fileServer_1 = require("./fileServer");
async function main() {
    console.log(`[STARTUP] Validating config...`);
    (0, config_1.validateConfig)();
    console.log(`[STARTUP] Config validated, mode=${config_1.config.mode}, rpc=${config_1.config.rpcUrl}`);
    const app = (0, express_1.default)();
    app.use(body_parser_1.default.json());
    app.get("/health", (_req, res) => {
        res.json({ status: "ok" });
    });
    // Mount based on mode
    if (config_1.config.mode === "claimguard") {
        console.log(`[STARTUP] Creating provider for claimguard mode...`);
        const provider = (0, blockchain_1.createProvider)();
        console.log(`[STARTUP] Provider created, loading routes...`);
        const { policyRouter } = await Promise.resolve().then(() => __importStar(require("./routes/policy")));
        const { measureRouter } = await Promise.resolve().then(() => __importStar(require("./routes/measure")));
        console.log(`[STARTUP] Routes loaded, mounting...`);
        app.use("/api", (0, access_1.accessRouter)(provider));
        app.use("/api", policyRouter());
        app.use("/api", measureRouter());
        console.log(`[STARTUP] Routes mounted`);
    }
    if (config_1.config.mode === "rbac") {
        app.use("/api", (0, rbac_1.rbacAccessRouter)());
    }
    if (config_1.config.mode === "hybrid") {
        const provider = (0, blockchain_1.createProvider)();
        app.use("/api", (0, hybrid_1.hybridAccessRouter)(provider));
    }
    // Start gateway on primary port
    console.log(`[STARTUP] Starting server on port ${config_1.config.port}...`);
    const server = app.listen(config_1.config.port, () => {
        console.log(`✓ ClaimGuard PEG (${config_1.config.mode}) listening on port ${config_1.config.port}`);
    });
    // Handle server errors
    server.on("error", (err) => {
        console.error(`[ERROR] Server error:`, err);
    });
    server.on("clientError", (err) => {
        console.error(`[ERROR] Client error:`, err);
    });
    // Set timeout for unresponsive requests
    server.setTimeout(30000);
    // Defer file server startup to next event loop iteration
    setImmediate(() => {
        try {
            console.log(`[STARTUP] Starting file server...`);
            const fileServer = (0, fileServer_1.createFileServer)();
            const fileServerInstance = fileServer.listen(5000, () => {
                console.log(`✓ File Server listening on port 5000`);
            });
            fileServerInstance.on("error", (err) => {
                console.error(`[ERROR] File server error:`, err);
            });
        }
        catch (err) {
            console.error(`[ERROR] Failed to start file server:`, err);
        }
    });
}
main().catch((err) => {
    console.error("PEG failed to start:", err);
    process.exit(1);
});
