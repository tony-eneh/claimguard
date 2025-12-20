import { createPublicClient, createWalletClient, http } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import type { Chain } from "viem";
import { config } from "./config";

// Select chain dynamically based on CHAIN_ID env
const chainId = Number(process.env.CHAIN_ID || 31337);

const hardhatChain = {
  id: 31337,
  name: "Hardhat",
  nativeCurrency: { name: "Ether", symbol: "ETH", decimals: 18 },
  rpcUrls: { default: { http: [config.rpcUrl] } },
} as const satisfies Chain;

const sepoliaChain = {
  id: 11155111,
  name: "Sepolia",
  nativeCurrency: { name: "Ether", symbol: "ETH", decimals: 18 },
  rpcUrls: { default: { http: [config.rpcUrl] } },
} as const satisfies Chain;

const selectedChain: Chain = chainId === 11155111 ? sepoliaChain : hardhatChain;

export const publicClient = createPublicClient({
  chain: selectedChain,
  transport: http(config.rpcUrl),
});

const account = privateKeyToAccount(config.gatewayPrivateKey as `0x${string}`);

export const walletClient = createWalletClient({
  account,
  chain: selectedChain,
  transport: http(config.rpcUrl),
});
