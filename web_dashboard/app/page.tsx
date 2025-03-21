"use client";
import { useState, useEffect, useCallback } from "react";
import { useAccount, useBalance } from "wagmi";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import axios from "axios";
import TokenChart from "./components/TokenChart";
import TradeControls from "./components/TradeControls";

// ✅ Supported chains (Same as backend)
const SUPPORTED_CHAINS: Record<string, number> = {
  ethereum: 1,
  avalanche: 43114,
  "avalanche-fuji": 43113,
  sepolia: 11155111,
};

export default function Home() {
  const { address, isConnected } = useAccount();
  const { data: balanceData } = useBalance({ address });

  // 🔴 HARD-CODED VALUES FOR TESTING
  const balance = "5.4321"; // Fake balance for testing
  const [selectedToken, setSelectedToken] = useState<string>("ethereum"); // Hardcoded token
  const [chainId, setChainId] = useState<number | null>(1); // Hardcoded Ethereum chain ID

  const [search, setSearch] = useState("");
  const [tokens, setTokens] = useState<any[]>([]);
  const [tokenData, setTokenData] = useState<any>({
    name: "Ethereum",
    symbol: "ETH",
    image: "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
    website: "https://ethereum.org/",
    market_cap: 300000000000,
    fdv: 320000000000,
    max_supply: "Infinite",
    predicted_price: "4100.25",
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // ✅ Fetch token data when token is selected
  useEffect(() => {
    if (selectedToken !== "ethereum") {
      fetchTokenData(selectedToken);
    }
  }, [selectedToken]);

  // ✅ Debounce search to limit API calls
  const fetchTokens = useCallback(async () => {
    if (search.length < 2) return;

    try {
      setLoading(true);
      const res = await axios.get(`https://api.coingecko.com/api/v3/search?query=${search}`);
      setTokens(res.data.coins || []);
    } catch (error) {
      console.error("Error fetching token data:", error);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      fetchTokens();
    }, 500); // Debounce API calls

    return () => clearTimeout(delayDebounce);
  }, [search, fetchTokens]);

  const fetchTokenData = async (tokenId: string) => {
    try {
      setLoading(true);
      setError(null);

      // Fetch token info
      const res = await axios.get(`http://127.0.0.1:8000/api/token-info/${tokenId}`);
      console.log("Token Info API Response:", res.data);

      if (res.data.error) throw new Error(res.data.error);

      // Fetch AI Predicted Price
      const aiRes = await axios.get(`http://127.0.0.1:8000/api/ai-predict/${tokenId}`);
      console.log("AI Predicted Price API Response:", aiRes.data);

      const tokenInfo = res.data;
      const detectedChainId = tokenInfo.chain_id?.toString() || "";
      console.log("Detected Chain ID:", detectedChainId);

      // ✅ Ensure we get a valid chainId from the supported list
      const validChainId = SUPPORTED_CHAINS[detectedChainId] ?? null;
      console.log("Valid Chain ID:", validChainId);

      setTokenData({
        ...tokenInfo,
        predicted_price: aiRes.data.predicted_price || "N/A",
      });

      setChainId(validChainId);
    } catch (error: any) {
      console.error("Error fetching token details:", error);
      setError("⚠️ Failed to fetch token details. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleTokenSelect = (tokenId: string) => {
    setSelectedToken(tokenId);
    setSearch("");
    setTokens([]);
  };

  return (
    <div className="min-h-screen bg-black text-green-400 flex flex-col p-6 font-mono">
      <div className="w-full flex justify-between items-center px-6">
        <h1 className="text-4xl font-bold text-green-500">⚡ Trading Hacker Bot ⚡</h1>
        <div className="flex flex-col items-end bg-green-900 px-4 py-2 rounded shadow-lg border border-green-500">
          <ConnectButton />
          {isConnected && <p className="text-sm mt-1 text-orange-400">Balance: {balance} ETH</p>}
        </div>
      </div>

      <div className="flex flex-col lg:flex-row w-full mt-8 gap-6">
        {/* ✅ Left Section: Token Chart */}
        <div className="w-full lg:w-3/4">
          <TokenChart tokenId={selectedToken} />
        </div>

        {/* ✅ Right Section: Search + Token Info + Buy/Sell */}
        <div className="w-full lg:w-1/4">
          {/* 🔍 Search Bar */}
          <div className="flex w-full">
            <input
              type="text"
              placeholder="🔎 Search token..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="p-2 rounded-l text-black w-full bg-green-200 focus:outline-none"
            />
          </div>

          {/* 🔍 Display Search Results */}
          {tokens.length > 0 && (
            <ul className="bg-green-900 mt-2 rounded border border-green-500">
              {tokens.map((token) => (
                <li
                  key={token.id}
                  onClick={() => handleTokenSelect(token.id)}
                  className="p-2 cursor-pointer hover:bg-green-700 text-white"
                >
                  <img src={token.thumb} alt={token.name} className="inline-block w-6 h-6 mr-2" />
                  {token.name} ({token.symbol.toUpperCase()})
                </li>
              ))}
            </ul>
          )}

          {/* ✅ Token Info Section */}
          {loading ? (
            <p className="text-gray-400 text-center mt-4">🔄 Loading token info...</p>
          ) : error ? (
            <p className="text-red-500 text-center mt-4">{error}</p>
          ) : tokenData ? (
            <div className="w-full bg-gray-900 p-4 rounded-lg shadow-md border border-blue-500 mt-4">
              <h2 className="text-xl font-bold text-white flex items-center">
                <img src={tokenData.image} alt={tokenData.name} className="w-6 h-6 mr-2" />
                {tokenData.name} ({tokenData.symbol.toUpperCase()})
              </h2>
              <p>
                🌍{" "}
                <a href={tokenData.website} target="_blank" className="text-blue-400">
                  Website
                </a>
              </p>
              <p>📊 Market Cap: ${tokenData.market_cap?.toLocaleString()}</p>
              <p>🏦 FDV: ${tokenData.fdv?.toLocaleString()}</p>
              <p>🔹 Max Supply: {tokenData.max_supply ?? "N/A"}</p>

              {/* ✅ AI Predicted Price */}
              <p className="text-yellow-400 text-lg mt-2">
                🔮 AI Predicted Price: ${tokenData.predicted_price ?? "N/A"}
              </p>

              {/* ✅ Render TradeControls with hardcoded chainId */}
              <TradeControls tokenId={selectedToken} chainId={chainId ?? 1} balance={balance} />
            </div>
          ) : (
            <p className="text-gray-400 text-center mt-4">🔎 Search for a token to view details.</p>
          )}
        </div>
      </div>
    </div>
  );
}
