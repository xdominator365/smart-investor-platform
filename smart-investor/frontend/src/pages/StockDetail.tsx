import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import {
  fetchStock,
  fetchSignal,
  fetchChartData,
  paperBuy,
  paperSell,
  paperAutoTrade,
} from "../api";

import StockCard from "../components/StockCard";
import SignalCard from "../components/SignalCard";
import PriceChart from "../components/Charts/PriceChart";
import RsiChart from "../components/Charts/RsiChart";
import PaperTradePanel from "../components/PaperTradePanel";

export default function StockDetail() {
  const { symbol } = useParams();
  const [stock, setStock] = useState<any>(null);
  const [signal, setSignal] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [quantity, setQuantity] = useState(1);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!symbol) return;

    fetchStock(symbol).then((res) => setStock(res.data));
    fetchSignal(symbol).then((res) => setSignal(res.data));
    fetchChartData(symbol).then((res) => setChartData(res.data));
  }, [symbol]);

  if (!symbol) {
    return (
      <p className="p-6 text-slate-500">
        No stock selected.
      </p>
    );
  }

  const handleBuy = async () => {
    await paperBuy(symbol, quantity);
    setMessage("Paper BUY executed");
  };

  const handleSell = async () => {
    await paperSell(symbol, quantity);
    setMessage("Paper SELL executed");
  };

  const handleAutoTrade = async () => {
    const res = await paperAutoTrade(symbol);
    setMessage(res.data.action);
  };

  return (
    <main className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
      {stock && <StockCard price={stock.current_price} symbol={symbol} />}

      {signal && (
        <SignalCard
          signal={signal.signal}
          confidence={signal.confidence}
          reason={signal.reason}
        />
      )}

      <PriceChart data={chartData} />
      <RsiChart data={chartData} />

      <PaperTradePanel
        quantity={quantity}
        setQuantity={setQuantity}
        onBuy={handleBuy}
        onSell={handleSell}
        onAutoTrade={handleAutoTrade}
        message={message}
      />
    </main>
  );
}
