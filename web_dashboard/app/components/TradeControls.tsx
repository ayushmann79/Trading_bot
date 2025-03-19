"use client";

import React, { useState } from "react";
import { useAccount, useBalance } from "wagmi";

const TradeControls = () => {
  const { address, isConnected } = useAccount();
  const { data: balanceData } = useBalance({ address });
  const balance = balanceData?.formatted ?? "0";
  const balanceNum = parseFloat(balance);
  const [amount, setAmount] = useState(0);

  const executeTrade = async (type: "buy" | "sell") => {
    if (!isConnected) {
      alert("Please connect your wallet first!");
      return;
    }
    if (type === "buy" && balanceNum < 0.01) {
      alert("Not enough balance to buy!");
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/${type}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: 1, amount: parseFloat(amount) }),
      });
      const data = await response.json();
      alert(data.message);
    } catch (error) {
      console.error(`Error executing ${type} trade:`, error);
      alert("Trade execution failed!");
    }
  };

  return (
    <div className="flex flex-col items-center gap-2 mt-4">
      <input
        type="number"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        placeholder="Enter Amount"
        className="p-2 border rounded text-black w-full"
      />

      <button onClick={() => executeTrade("buy")} className="px-4 py-2 bg-green-500 hover:bg-green-700 rounded w-full">
        BUY
      </button>

      <button onClick={() => executeTrade("sell")} className="px-4 py-2 bg-red-500 hover:bg-red-700 rounded w-full">
        SELL
      </button>
    </div>
  );
};

export default TradeControls;
