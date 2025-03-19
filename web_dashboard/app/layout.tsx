import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import "@rainbow-me/rainbowkit/styles.css";
import WagmiSetupProvider from "./components/WagmiProvider"; // ✅ Import Wagmi setup

// Font configurations
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Metadata
export const metadata: Metadata = {
  title: "AI Trading Bot Dashboard",
  description: "AI-powered trading bot with Web3 wallet integration",
};

// ✅ RootLayout Component
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <WagmiSetupProvider>{children}</WagmiSetupProvider> {/* ✅ Use the new WagmiProvider */}
      </body>
    </html>
  );
}
