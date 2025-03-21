import { useState, useEffect, useMemo } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// ✅ Register Chart.js components
Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface TokenChartProps {
  tokenId: string;
}

export default function TokenChart({ tokenId }: TokenChartProps) {
  const [timeRange, setTimeRange] = useState("7");
  const [chartData, setChartData] = useState<any>(null);
  const [tokenInfo, setTokenInfo] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [retry, setRetry] = useState<number>(0);

  useEffect(() => {
    let isMounted = true;

    async function fetchData() {
      if (!tokenId) return;
      setLoading(true);
      setError(null);

      try {
        const [chartRes, infoRes, aiRes] = await Promise.all([
          axios.get(`http://localhost:8000/api/token-chart/${tokenId}`, {
            params: { days: timeRange === "all" ? "max" : timeRange },
            headers: { "Cache-Control": "no-cache" },
          }),
          axios.get(`http://localhost:8000/api/token-info/${tokenId}`),
          axios.get(`http://localhost:8000/api/ai-predict/${tokenId}`), // ✅ AI Predicted Price
        ]);

        // ✅ Handle rate limit (429) gracefully
        if (chartRes.status === 429) {
          setError("⚠️ Rate limit exceeded. Please try again later.");
          return;
        }

        // ✅ Ensure price data exists before updating state
        if (!chartRes.data?.prices || chartRes.data.prices.length === 0) {
          setError("⚠️ No price data available for this token.");
          return;
        }

        const prices = chartRes.data.prices.map((entry: any) => ({
          timestamp: new Date(entry[0]).toLocaleString(),
          price: entry[1],
        }));

        if (isMounted) {
          setChartData({
            labels: prices.map((p) => p.timestamp),
            datasets: [
              {
                label: `${tokenId.toUpperCase()} Price (USD)`,
                data: prices.map((p) => p.price),
                borderColor: "#4CAF50",
                backgroundColor: "rgba(76, 175, 80, 0.2)",
                borderWidth: 2,
                pointRadius: 3,
                fill: true,
                tension: 0.3,
              },
            ],
          });

          // ✅ Merge AI prediction into token info
          setTokenInfo({
            ...infoRes.data,
            predicted_price: aiRes.data.predicted_price || "N/A",
          });
        }
      } catch (err: any) {
        console.error("Error fetching data:", err);
        if (isMounted) {
          setError("⚠️ Failed to load chart data.");
          if (retry < 2) {
            setRetry(retry + 1);
          }
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    fetchData();
    return () => {
      isMounted = false;
    };
  }, [tokenId, timeRange, retry]);

  const chartOptions = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { display: true },
        y: {
          beginAtZero: false,
          ticks: {
            callback: function (value: number) {
              return "$" + value.toLocaleString();
            },
          },
        },
      },
    }),
    []
  );

  return (
    <div className="p-4 bg-gray-800 rounded-lg shadow-md border border-green-500 w-full">
      <div className="flex justify-between mb-4">
        <h2 className="text-white text-lg">{tokenId.toUpperCase()} Price Chart</h2>
        <select
          value={timeRange}
          onChange={(e) => {
            setTimeRange(e.target.value);
            setError(null);
          }}
          className="bg-black text-green-400 border border-green-500 px-2 py-1 rounded"
        >
          <option value="1">1 Day</option>
          <option value="7">7 Days</option>
          <option value="30">1 Month</option>
          <option value="365">1 Year</option>
          <option value="all">All Time</option>
        </select>
      </div>

      {/* ✅ AI Price Prediction Display */}
      {tokenInfo?.predicted_price && (
        <p className="text-blue-400 text-center text-lg">
          🔮 AI Predicted Price: ${tokenInfo.predicted_price}
        </p>
      )}

      {loading ? (
        <p className="text-gray-400 text-center">🔄 Loading chart data...</p>
      ) : error ? (
        <p className="text-red-500 text-center">{error}</p>
      ) : (
        <div className="relative w-full h-96">
          <Line data={chartData} options={chartOptions} />
        </div>
      )}
    </div>
  );
}
