"use client";
import { useState, useEffect } from "react";
import { useAccount, useBalance } from "wagmi";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import axios from "axios";
import TokenChart from "./components/TokenChart";
import TradeControls from "./components/TradeControls";

export default function Home() {
  const { address, isConnected } = useAccount();
  const { data: balanceData } = useBalance({ address });
  const balance = balanceData?.formatted ?? "0";

  const [ethPrice, setEthPrice] = useState<number | null>(null);
  const [trades, setTrades] = useState([]);
  const [search, setSearch] = useState("");
  const [tokens, setTokens] = useState<any[]>([]);
  const [selectedToken, setSelectedToken] = useState("avalanche-2"); // Default to AVAX
  const [tokenData, setTokenData] = useState<any>(null);

  // Fetch ETH price and trade history
  useEffect(() => {
    async function fetchData() {
      try {
        const ethPriceRes = await axios.get("http://127.0.0.1:8000/api/prices/ethereum");
        setEthPrice(ethPriceRes.data.ethereum.usd);

        const tradesRes = await axios.get("http://127.0.0.1:8000/api/trades");
        setTrades(tradesRes.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    }

    fetchData();
  }, []);

  // Fetch default AVAX token data on mount
  useEffect(() => {
    fetchTokenData(selectedToken);
  }, []);

  // Fetch tokens based on search input
  const fetchTokens = async () => {
    if (search.length < 2) return;

    try {
      const res = await axios.get(`https://api.coingecko.com/api/v3/search?query=${search}`);
      setTokens(res.data.coins);
    } catch (error) {
      console.error("Error fetching token data:", error);
    }
  };

  // Fetch selected token details
  const fetchTokenData = async (tokenId: string) => {
    try {
      const res = await axios.get(`https://api.coingecko.com/api/v3/coins/${tokenId}`);
      setTokenData(res.data);
    } catch (error) {
      console.error("Error fetching token details:", error);
    }
  };

  // Handle token selection
  const handleTokenSelect = (tokenId: string) => {
    setSelectedToken(tokenId);
    setSearch("");
    setTokens([]);
    fetchTokenData(tokenId);
  };

  // Handle Enter key press for search
  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      fetchTokens();
    }
  };

  return (
    <div className="min-h-screen bg-black text-green-400 flex flex-col p-6 font-mono">
      
      {/* 🟢 Top Section (Title + Wallet Info) */}
      <div className="w-full flex justify-between items-center px-6">
        <h1 className="text-4xl font-bold text-green-500">⚡ Trading Hacker Bot ⚡</h1>
        <div className="flex flex-col items-end bg-green-900 px-4 py-2 rounded shadow-lg border border-green-500">
          <ConnectButton />
          {isConnected && (
            <p className="text-sm mt-1 text-orange-400">Balance: {balance} ETH</p>
          )}
        </div>
      </div>

      {/* 🔄 Main Layout */}
      <div className="flex flex-col lg:flex-row w-full mt-8 gap-6">
        
        {/* 📈 Left Section: Chart + Trade History */}
        <div className="w-full lg:w-3/4">
          <TokenChart tokenId={selectedToken} />

          {/* 📜 Trade History */}
          <div className="mt-6 w-full bg-green-950 p-4 rounded border border-green-500">
            <h2 className="text-2xl text-white text-center">📜 Trade History</h2>
            <div className="w-full mt-2 overflow-x-auto border border-green-500 rounded">
              <table className="w-full">
                <thead className="bg-green-800 text-white">
                  <tr>
                    <th className="p-2">Token</th>
                    <th className="p-2">Amount</th>
                    <th className="p-2">Price</th>
                    <th className="p-2">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.length > 0 ? trades.map((trade, index) => (
                    <tr key={index} className="text-white even:bg-green-900 odd:bg-black">
                      <td className="p-2">{trade.token}</td>
                      <td className="p-2">{trade.amount}</td>
                      <td className="p-2 text-orange-400">${trade.price.toFixed(2)}</td>
                      <td className="p-2 text-red-400">{trade.timestamp}</td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan={4} className="p-4 text-center text-gray-400">
                        No trade history available.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* 🔍 Right Section: Search + Token Info + Buy/Sell */}
        <div className="w-full lg:w-1/4">
          
          {/* 🔍 Search Bar */}
          <div className="flex w-full">
            <input
              type="text"
              placeholder="🔎 Search token..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={handleKeyDown}
              className="p-2 rounded-l text-black w-full bg-green-200 focus:outline-none"
            />
            <button
              onClick={fetchTokens}
              className="bg-green-500 text-black px-4 py-2 rounded-r hover:bg-green-700"
            >
              Search
            </button>
          </div>

          {/* 🔽 Token Search Results */}
          {tokens.length > 0 && (
            <ul className="bg-green-900 text-orange-400 rounded mt-2 max-w-lg border border-green-600 shadow-lg">
              {tokens.slice(0, 5).map((token) => (
                <li
                  key={token.id}
                  className="p-2 cursor-pointer hover:bg-green-700 hover:text-white"
                  onClick={() => handleTokenSelect(token.id)}
                >
                  {token.name} ({token.symbol.toUpperCase()})
                </li>
              ))}
            </ul>
          )}

          {/* 📜 Token Information */}
          {tokenData && (
            <div className="w-full bg-gray-900 p-4 rounded-lg shadow-md border border-blue-500 mt-4">
              <h2 className="text-xl font-bold text-white flex items-center">
                <img src={tokenData.image?.small} alt={tokenData.name} className="w-6 h-6 mr-2" />
                {tokenData.name} ({tokenData.symbol.toUpperCase()})
              </h2>
              <p>🌍 <a href={tokenData.links?.homepage[0]} target="_blank" className="text-blue-400">Website</a></p>
              <p>📊 Market Cap: ${tokenData.market_data?.market_cap?.usd.toLocaleString()}</p>
              <p>🏦 FDV: ${tokenData.market_data?.fully_diluted_valuation?.usd?.toLocaleString()}</p>
              <p>🔹 Max Supply: {tokenData.market_data?.max_supply ?? "N/A"}</p>
            </div>
          )}

          {/* 🟢 Buy/Sell Buttons */}
          <div className="mt-4">
            <TradeControls />
          </div>
        </div>
      </div>
    </div>
  );
}
