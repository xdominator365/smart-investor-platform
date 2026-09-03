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
  getZerodhaLoginUrl,
  fetchZerodhaStatus,
  previewZerodhaOrder,
  placeZerodhaOrder,
  connectMarketStream,
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
  const [zerodhaConnected, setZerodhaConnected] = useState(false);
  const [zerodhaMessage, setZerodhaMessage] = useState("");
  const [zerodhaPreview, setZerodhaPreview] = useState<any>(null);

  useEffect(() => {
    fetchZerodhaStatus()
      .then((res) => setZerodhaConnected(res.data.connected))
      .catch(() => setZerodhaConnected(false));
  }, []);

  const connectZerodha = async () => {
    try {
      const response = await getZerodhaLoginUrl();
      window.location.assign(response.data.login_url);
    } catch {
      setZerodhaMessage("Zerodha connection is not configured");
    }
  };

  const previewLiveOrder = async () => {
    if (!symbol || !signal || !stock) return;
    if (signal.signal !== "BUY" && signal.signal !== "SELL") return;

    try {
      const response = await previewZerodhaOrder({
        symbol,
        side: signal.signal,
        quantity,
        reference_price: Number(stock.current_price),
      });
      setZerodhaPreview(response.data);
      setZerodhaMessage("");
    } catch (error: any) {
      setZerodhaPreview(null);
      setZerodhaMessage(
        error?.response?.data?.detail || "Unable to preview Zerodha order",
      );
    }
  };

  const placeLiveOrder = async () => {
    if (!zerodhaPreview?.preview_id) return;
    const confirmed = window.confirm(
      `Place LIVE ${zerodhaPreview.side} order for ${zerodhaPreview.quantity} ${zerodhaPreview.symbol}?`,
    );
    if (!confirmed) return;

    try {
      const response = await placeZerodhaOrder({
        preview_id: zerodhaPreview.preview_id,
        idempotency_key: crypto.randomUUID(),
        confirmed: true,
      });
      setZerodhaMessage(`Zerodha order submitted: ${response.data.status}`);
      setZerodhaPreview(null);
    } catch (error: any) {
      setZerodhaMessage(
        error?.response?.data?.detail || "Unable to place Zerodha order",
      );
    }
  };

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

    fetchNewsInsights(symbol)
    .then(res => setNewsInsights(res.data))
    .catch(() => setNewsInsights(null));

    const stream = connectMarketStream([symbol], (message) => {
      if (message?.type !== "market_update") return;
      if (!message?.symbol || message.symbol.toUpperCase() !== symbol.toUpperCase()) return;

      setStock((current: any) => ({
        ...(current ?? {}),
        ...(message.data ?? {}),
        symbol: (message.data?.symbol || symbol).toUpperCase(),
      }));
    });

    return () => stream.close();
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
          signal={signal?.signal}
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

      <div className="trading-card col-span-1 md:col-span-2">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="metric-label">Live broker</p>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
              {zerodhaConnected
                ? "Zerodha account connected"
                : "Connect Zerodha before placing live orders"}
            </p>
          </div>
          <button
            type="button"
            onClick={connectZerodha}
            className="rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 px-5 py-2.5 text-sm font-bold text-white"
          >
            {zerodhaConnected ? "Reconnect Zerodha" : "Connect Zerodha"}
          </button>
        </div>
        {signal && (signal.signal === "BUY" || signal.signal === "SELL") && (
          <div className="mt-5 border-t border-slate-200 pt-5 dark:border-slate-700">
            <p className="text-sm text-slate-600 dark:text-slate-300">
              AI signal: <strong>{signal.signal}</strong>. Review a Zerodha order preview before any live execution.
            </p>
            <button
              type="button"
              onClick={previewLiveOrder}
              disabled={!zerodhaConnected || !marketOpen || quantity < 1}
              className="mt-3 rounded-xl border border-sky-500 px-4 py-2.5 text-sm font-bold text-sky-600 disabled:cursor-not-allowed disabled:opacity-50 dark:text-sky-300"
            >
              Preview {signal.signal} Order
            </button>
          </div>
        )}
        {signal?.signal === "HOLD" && (
          <p className="mt-5 border-t border-slate-200 pt-5 text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
            HOLD does not create a live order preview.
          </p>
        )}
        {zerodhaPreview && (
          <div className="mt-4 rounded-xl border border-sky-500/30 bg-sky-500/5 p-4 text-sm text-slate-600 dark:text-slate-200">
            <p className="font-bold">Order preview only</p>
            <p className="mt-2">{zerodhaPreview.side} {zerodhaPreview.quantity} {zerodhaPreview.symbol} on {zerodhaPreview.exchange}</p>
            <p>Type: {zerodhaPreview.order_type} | Product: {zerodhaPreview.product}</p>
            <p>Estimated value: ₹ {zerodhaPreview.estimated_value}</p>
            <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">No order has been sent to Zerodha.</p>
            <button
              type="button"
              onClick={placeLiveOrder}
              className="mt-4 rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-bold text-white"
            >
              Place Live Order
            </button>
          </div>
        )}
        {zerodhaMessage && (
          <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
            {zerodhaMessage}
          </p>
        )}
      </div>

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
