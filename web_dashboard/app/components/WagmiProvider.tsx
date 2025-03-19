"use client"; // ✅ Ensure it runs only on the client

import "@rainbow-me/rainbowkit/styles.css";
import { getDefaultConfig, RainbowKitProvider } from "@rainbow-me/rainbowkit";
import { WagmiProvider } from "wagmi"; // ✅ Imported WagmiProvider (Don't rename this import)
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { mainnet, sepolia } from "wagmi/chains";
import { http } from "wagmi";

// ✅ Replace with your actual WalletConnect Project ID
const WALLETCONNECT_PROJECT_ID = "033448f66d2e7f0837d3a79d12d935c7";

// ✅ Define Avalanche Chains (Mainnet & Fuji Testnet)
const avalancheMainnet = {
  id: 43114, // ✅ Avalanche C-Chain Mainnet
  name: "Avalanche Mainnet",
  nativeCurrency: { name: "AVAX", symbol: "AVAX", decimals: 18 },
  rpcUrls: { default: { http: ["https://avax-mainnet.g.alchemy.com/v2/E0kslGCP2sybcaysG2DEMzIOKQKBeYP-"] } },
  blockExplorers: { default: { name: "Snowtrace", url: "https://snowtrace.io/" } },
};

const avalancheFuji = {
  id: 43113, // ✅ Avalanche Fuji Testnet
  name: "Avalanche Fuji Testnet",
  nativeCurrency: { name: "AVAX", symbol: "AVAX", decimals: 18 },
  rpcUrls: { default: { http: ["https://avax-fuji.g.alchemy.com/v2/E0kslGCP2sybcaysG2DEMzIOKQKBeYP-"] } },
  blockExplorers: { default: { name: "Snowtrace", url: "https://testnet.snowtrace.io/" } },
};

// ✅ Define Supported Chains (Ethereum + Avalanche)
const chains = [mainnet, sepolia, avalancheMainnet, avalancheFuji];

// ✅ Create Wagmi Config with Alchemy RPC Transports
const wagmiConfig = getDefaultConfig({
  appName: "AI Trading Bot",
  projectId: WALLETCONNECT_PROJECT_ID,
  chains,
  ssr: true, // ✅ Prevents SSR Errors in Next.js
  transports: {
    [mainnet.id]: http("https://eth-mainnet.g.alchemy.com/v2/E0kslGCP2sybcaysG2DEMzIOKQKBeYP-"),
    [sepolia.id]: http("https://eth-sepolia.g.alchemy.com/v2/E0kslGCP2sybcaysG2DEMzIOKQKBeYP-"),
    [avalancheMainnet.id]: http("https://avax-mainnet.g.alchemy.com/v2/E0kslGCP2sybcaysG2DEMzIOKQKBeYP-"),
    [avalancheFuji.id]: http("https://avax-fuji.g.alchemy.com/v2/E0kslGCP2sybcaysG2DEMzIOKQKBeYP-"),
  },
});

// ✅ Create Query Client
const queryClient = new QueryClient();

export default function WagmiSetupProvider ({ children }: { children: React.ReactNode }) {
  return (
    <WagmiProvider config={wagmiConfig}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider chains={chains}>{children}</RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
}
