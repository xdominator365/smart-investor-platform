import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import {
  fetchStock,
  fetchSignal,
  fetchChartData,
  paperBuy,
  paperSell,
  paperAutoTrade,
  fetchMarketStatusAPI,
  fetchAutoTradeDecisions,
  fetchNewsInsights,
} from "../api";

import StockCard from "../components/StockCard";
import SignalCard from "../components/SignalCard";
import PriceChart from "../components/Charts/PriceChart";
import RsiChart from "../components/Charts/RsiChart";
import PaperTradePanel from "../components/PaperTradePanel";
import AutoTradeExplainability from "../components/AutoTradeExplainability"
import NewsInsightCard from "../components/NewsInsightsCard";


export default function StockDetail() {
  const { symbol } = useParams<{ symbol: string }>();

  const [stock, setStock] = useState<any>(null);
  const [signal, setSignal] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [quantity, setQuantity] = useState(1);
  const [message, setMessage] = useState("");
  const [marketOpen, setMarketOpen] = useState(false);
  const [decisions, setDecisions] = useState<any[]>([]);
  const [newsInsights, setNewsInsights] = useState<any>(null);

  // fetch market open/close status
  useEffect(() => {
    fetchMarketStatusAPI()
      .then((res) => setMarketOpen(res.data.market_open))
      .catch(() => {});
  }, []);

  // fetch stock data once per symbol
  useEffect(() => {
    if (!symbol) return;
    fetchStock(symbol).then((res) => setStock(res.data));
    fetchSignal(symbol).then((res) => setSignal(res.data));
    fetchChartData(symbol).then((res) => setChartData(res.data));
    fetchAutoTradeDecisions(symbol).then(res => setDecisions(res.data));
    loadAutoTradeDecisions();

    // NEW: fetch news insights
    fetchNewsInsights(symbol)
    .then(res => setNewsInsights(res.data))
    .catch(() => setNewsInsights(null));

  }, [symbol]);

  if (!symbol) {
    return <p className="p-6 text-slate-500">No stock selected.</p>;
  }

  const handleBuy = async () => {
    if (!marketOpen) {
      setMessage("⏹️ Please place your order when the market is open.");
      return;
    }
    await paperBuy(symbol, quantity);
    setMessage("Paper BUY executed");
  };

  const handleSell = async () => {
    if (!marketOpen) {
      setMessage("⏹️ Please place your order when the market is open.");
      return;
    }
    await paperSell(symbol, quantity);
    setMessage("Paper SELL executed");
  };

  const handleAutoTrade = async () => {
    if (!marketOpen) {
      setMessage("⏹️ Please place your order when the market is open.");
      return;
    }
    const res = await paperAutoTrade(symbol);
    setMessage(res.data.action);
    await loadAutoTradeDecisions();
  };

  const loadAutoTradeDecisions = async () => {
  if (!symbol) return;
  const res = await fetchAutoTradeDecisions(symbol);
  setDecisions(res.data);
  };


  return (
    <main className="w-full max-w-full min-w-0 p-4 md:p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
      {stock && (
        <StockCard
          price={stock.current_price}
          symbol={symbol}
          ma20={signal?.ma_20}
          ma50={signal?.ma_50}
        />
      )}

      {signal && (
        <SignalCard
          signal={signal.signal}
          confidence={signal.confidence}
          reason={signal.reason}
        />
      )}

      {/*NEW: News Insights */}
      <NewsInsightCard insight={newsInsights} />
  
      <PriceChart data={chartData} />
      <RsiChart data={chartData} />

      <PaperTradePanel
        quantity={quantity}
        setQuantity={setQuantity}
        onBuy={handleBuy}
        onSell={handleSell}
        onAutoTrade={handleAutoTrade}
        message={message}
        marketOpen={marketOpen}
      />
      <AutoTradeExplainability decisions={decisions} />
    </main>
  );
}
