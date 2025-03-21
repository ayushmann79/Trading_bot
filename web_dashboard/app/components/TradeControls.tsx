import { useEffect, useState } from "react";
import { ethers } from "ethers";

const SUPPORTED_CHAINS: Record<string, number> = {
  ethereum: 1,
  avalanche: 43114,
  "avalanche-fuji": 43113,
  sepolia: 11155111,
};

const TOKEN_ABI = [
  "function buy() payable",
  "function sell(uint256 amount) public",
];

type TradeControlsProps = {
  tokenId: string;
  chainId: number;
  balance: string;
};

const TradeControls: React.FC<TradeControlsProps> = ({ tokenId, chainId, balance }) => {
  const [userChainId, setUserChainId] = useState<number | null>(null);
  const [amount, setAmount] = useState<string>("");
  const [stopLoss, setStopLoss] = useState<number>(5); // Default 5%
  const [takeProfit, setTakeProfit] = useState<number>(10); // Default 10%
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function getNetwork() {
      if (!window.ethereum) {
        setError("MetaMask not detected!");
        return;
      }

      const provider = new ethers.BrowserProvider(window.ethereum);
      const { chainId } = await provider.getNetwork();
      setUserChainId(Number(chainId));
    }

    getNetwork();
  }, []);

  const switchNetwork = async () => {
    if (!window.ethereum) {
      setError("MetaMask not detected!");
      return;
    }

    try {
      await window.ethereum.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: ethers.toBeHex(chainId) }],
      });
      setUserChainId(chainId);
      setError(null);
    } catch (error) {
      console.error("Network switch failed:", error);
      setError("Please switch the network manually in MetaMask.");
    }
  };

  const validateAmount = () => {
    const amt = parseFloat(amount);
    if (isNaN(amt) || amt <= 0) {
      setError("Invalid amount! Must be greater than 0.");
      return false;
    }
    if (amt > parseFloat(balance)) {
      setError("Insufficient balance!");
      return false;
    }
    setError(null);
    return true;
  };

  const buyToken = async () => {
    if (!validateAmount()) return;
    if (!userChainId || userChainId !== chainId) {
      setError("Wrong network! Please switch.");
      return;
    }

    try {
      setLoading(true);
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const tokenContract = new ethers.Contract(tokenId, TOKEN_ABI, signer);

      const tx = await tokenContract.buy({
        value: ethers.parseEther(amount),
      });

      await tx.wait();
      alert("✅ Token purchased successfully!");
    } catch (error) {
      console.error("Transaction failed:", error);
      setError("⚠️ Transaction failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const sellToken = async () => {
    if (!validateAmount()) return;
    if (!userChainId || userChainId !== chainId) {
      setError("Wrong network! Please switch.");
      return;
    }

    try {
      setLoading(true);
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const tokenContract = new ethers.Contract(tokenId, TOKEN_ABI, signer);

      const tx = await tokenContract.sell(ethers.parseEther(amount));
      await tx.wait();

      alert("✅ Token sold successfully!");
    } catch (error) {
      console.error("Transaction failed:", error);
      setError("⚠️ Transaction failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 p-4 rounded-lg shadow-md border border-gray-700 mt-4">
      <h3 className="text-lg text-white text-center mb-2">Trade {tokenId.toUpperCase()}</h3>

      {error && <p className="text-red-500 text-center">{error}</p>}

      {/* Amount Input */}
      <input
        type="number"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        placeholder="Enter amount"
        className="w-full p-2 rounded text-black border border-gray-500"
      />

      {/* Stop-Loss Slider */}
      <div className="mt-2">
        <label className="text-white">Stop-Loss: {stopLoss}%</label>
        <input
          type="range"
          min="1"
          max="50"
          value={stopLoss}
          onChange={(e) => setStopLoss(parseInt(e.target.value))}
          className="w-full"
        />
      </div>

      {/* Take-Profit Slider */}
      <div className="mt-2">
        <label className="text-white">Take-Profit: {takeProfit}%</label>
        <input
          type="range"
          min="1"
          max="50"
          value={takeProfit}
          onChange={(e) => setTakeProfit(parseInt(e.target.value))}
          className="w-full"
        />
      </div>

      {/* Buy/Sell Buttons */}
      <div className="flex justify-between mt-4">
        <button
          onClick={buyToken}
          className={`px-4 py-2 rounded ${
            userChainId === chainId && !loading ? "bg-green-500 hover:bg-green-700" : "bg-gray-600 cursor-not-allowed"
          }`}
          disabled={userChainId !== chainId || loading}
        >
          {loading ? "Processing..." : "Buy"}
        </button>
        <button
          onClick={sellToken}
          className={`px-4 py-2 rounded ${
            userChainId === chainId && !loading ? "bg-red-500 hover:bg-red-700" : "bg-gray-600 cursor-not-allowed"
          }`}
          disabled={userChainId !== chainId || loading}
        >
          {loading ? "Processing..." : "Sell"}
        </button>
      </div>

      {/* Change Network Button */}
      {userChainId !== chainId && (
        <div className="mt-4 text-center">
          <p className="text-yellow-400">⚠️ Wrong network!</p>
          <button onClick={switchNetwork} className="bg-blue-500 px-4 py-2 rounded mt-2">
            Change Network
          </button>
        </div>
      )}
    </div>
  );
};

export default TradeControls;
