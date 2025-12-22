import { useState, useEffect } from "react";
import {
  fetchStock,
  fetchSignal,
  fetchChartData,
  paperBuy,
  paperSell,
  paperAutoTrade,
  fetchPortfolio,
} from "./api";

import Header from "./components/Header";
import SymbolSearch from "./components/SymbolSearch";
import SignalCard from "./components/SignalCard";
import StockCard from "./components/StockCard";
import PriceChart from "./components/Charts/PriceChart";
import RsiChart from "./components/Charts/RsiChart";
import PaperTradePanel from "./components/PaperTradePanel";
import PortfolioSummary from "./components/PortfolioSummary";
import TradeHistoryTable from "./components/TradeHistoryTable";
import PortfolioHoldingsTable from "./components/PortfolioHoldingsTable";

export default function App() {
  const [theme, setTheme] = useState<"dark" | "light">("light");
  const [symbol, setSymbol] = useState("TCS.NS");
  const [stock, setStock] = useState<any>(null);
  const [signal, setSignal] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [quantity, setQuantity] = useState(1);
  const [portfolio, setPortfolio] = useState<any>(null);
  const [message, setMessage] = useState("");
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [prices, setPrices] = useState<Record<string, number>>({});

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  useEffect(() => {
  if (!autoRefresh) return;

  const interval = setInterval(() => {
    loadData();
  }, 10000); // 10 seconds

  return () => clearInterval(interval);
  }, [autoRefresh, symbol]);


  const loadData = async () => {
    const stockRes = await fetchStock(symbol);
    const signalRes = await fetchSignal(symbol);
    const chartRes = await fetchChartData(symbol);
    const portfolioRes = await fetchPortfolio();

    setStock(stockRes.data);
    setSignal(signalRes.data);
    setChartData(chartRes.data);
    setPortfolio(portfolioRes.data);

    if (portfolioRes.data?.holdings?.length > 0) {
    loadHoldingPrices(portfolioRes.data.holdings);
    }
  };

  const handleBuy = async () => {
    await paperBuy(symbol, quantity);
    setMessage("Paper BUY executed");
    loadData();
  };

  const handleSell = async () => {
    await paperSell(symbol, quantity);
    setMessage("Paper SELL executed");
    loadData();
  };

  const handleAutoTrade = async () => {
  const res = await paperAutoTrade(symbol);
  setMessage(res.data.action);
  loadData();
  };

  const loadHoldingPrices = async (holdings: any[]) => {
  const priceMap: Record<string, number> = {};

  for (const h of holdings) {
    const res = await fetchStock(h.symbol);
    priceMap[h.symbol] = res.data.current_price;
    }

    setPrices(priceMap);
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-900 transition-colors">
      <Header
        theme={theme}
        onToggleTheme={() =>
          setTheme(theme === "dark" ? "light" : "dark")
        }
      />

      <SymbolSearch
        symbol={symbol}
        setSymbol={setSymbol}
        onFetch={loadData}
      />

      <div className="px-6 flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={autoRefresh}
          onChange={() => setAutoRefresh(!autoRefresh)}
        />
        <span>Auto refresh every 10s</span>
      </div>

      {stock && signal && (
        <main className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <SignalCard
            signal={signal.signal}
            confidence={signal.confidence}
            reason={signal.reason}
          />

          <StockCard
            price={stock.current_price}
            symbol={stock.symbol}
          />

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

          {portfolio && (
            <>
              <PortfolioSummary portfolio={portfolio} />
              <PortfolioHoldingsTable holdings={portfolio.holdings} prices={prices} />
              <TradeHistoryTable trades={portfolio.trade_history} />
            </>
          )}

        </main>
      )}
    </div>
  );
}
