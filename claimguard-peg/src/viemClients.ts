import { createPublicClient, createWalletClient, http } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import type { Chain } from "viem";
import { config } from "./config";

// Define your local Hardhat/PureChain chain
// adjust id/name if you use a different chainId
const localChain = {
  id: 31337,
  name: "Hardhat",
  nativeCurrency: { name: "Ether", symbol: "ETH", decimals: 18 },
  rpcUrls: {
    default: { http: [config.rpcUrl] },
  },
} as const satisfies Chain;

export const publicClient = createPublicClient({
  chain: localChain,
  transport: http(config.rpcUrl),
});

const account = privateKeyToAccount(config.gatewayPrivateKey as `0x${string}`);

export const walletClient = createWalletClient({
  account,
  chain: localChain,
  transport: http(config.rpcUrl),
});
