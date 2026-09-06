import { useEffect, useMemo, useState } from "react";
import {
  fetchPortfolio,
  fetchStock,
  fetchMarketStatusAPI,
  fetchBotStatus,
  toggleBot,
  setBotStrategy,
  fetchStrategies
} from "../api";

import PortfolioSummary from "../components/PortfolioSummary";
import PortfolioHoldingsTable from "../components/PortfolioHoldingsTable";
import TradeHistoryTable from "../components/TradeHistoryTable";

export default function Dashboard() {
  const [portfolio, setPortfolio] = useState<any>(null);
  const [isBotEnabled, setIsBotEnabled] = useState(false);
  const [botStrategyId, setBotStrategyId] = useState("trend_follower");
  const [strategies, setStrategies] = useState<any[]>([]);
  const [prices, setPrices] = useState<Record<string, {
    current_price: number;
    return_1d: number;
    return_5d: number;
    return_30d: number;
  }>>({});
  const [marketOpen, setMarketOpen] = useState(false);

  const portfolioPerformance = useMemo(() => {
    if (!portfolio?.holdings?.length) {
      return { return_1d: 0, return_5d: 0, return_30d: 0 };
    }

    let totalInvested = 0;
    let weightedReturn1d = 0;
    let weightedReturn5d = 0;
    let weightedReturn30d = 0;

    portfolio.holdings.forEach((holding: any) => {
      const snapshot = prices[holding.symbol] ?? {
        current_price: holding.avg_price,
        return_1d: 0,
        return_5d: 0,
        return_30d: 0,
      };
      const invested = (holding.quantity ?? 0) * (holding.avg_price ?? 0);
      totalInvested += invested;
      weightedReturn1d += (snapshot.return_1d ?? 0) * invested;
      weightedReturn5d += (snapshot.return_5d ?? 0) * invested;
      weightedReturn30d += (snapshot.return_30d ?? 0) * invested;
    });

    return {
      return_1d: totalInvested ? weightedReturn1d / totalInvested : 0,
      return_5d: totalInvested ? weightedReturn5d / totalInvested : 0,
      return_30d: totalInvested ? weightedReturn30d / totalInvested : 0,
    };
  }, [portfolio, prices]);

  // Load portfolio and bot data on initial render
  useEffect(() => {
    fetchPortfolio().then((res) => setPortfolio(res.data));
    fetchStrategies().then((res) => setStrategies(res.data.strategies));
    fetchBotStatus().then((res) => {
      setIsBotEnabled(res.data.is_bot_enabled);
      setBotStrategyId(res.data.bot_strategy_id);
    });
  }, []);

  const handleToggleBot = async () => {
    const newVal = !isBotEnabled;
    setIsBotEnabled(newVal);
    await toggleBot(newVal);
  };

  const handleStrategyChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newStrategy = e.target.value;
    setBotStrategyId(newStrategy);
    await setBotStrategy(newStrategy);
  };

  // Poll market open/close status
  useEffect(() => {
    const fetchMarketStatus = async () => {
      try {
        const res = await fetchMarketStatusAPI();
        setMarketOpen(res.data.market_open);
      } catch {}
    };

    fetchMarketStatus();
    const interval = setInterval(fetchMarketStatus, 60_000);
    return () => clearInterval(interval);
  }, []);

  // Fetch latest prices for all holdings
  const fetchPricesForHoldings = async (
    holdings: any[],
    cancelledRef: { current: boolean }
  ) => {
    const symbols = holdings.map((h) => h.symbol);
    if (!symbols.length) return;

    const results = await Promise.all(
      symbols.map((symbol) =>
        fetchStock(symbol)
          .then((res) => [symbol, res.data] as [string, any])
          .catch(() => [symbol, null])
      )
    );

    if (cancelledRef.current) return;

    const fetchedPrices: Record<string, {
      current_price: number;
      return_1d: number;
      return_5d: number;
      return_30d: number;
    }> = {};

    results.forEach(([symbol, stockData]) => {
      if (stockData && typeof stockData.current_price === "number") {
        fetchedPrices[symbol] = {
          current_price: stockData.current_price,
          return_1d: Number(stockData.return_1d ?? 0),
          return_5d: Number(stockData.return_5d ?? 0),
          return_30d: Number(stockData.return_30d ?? 0),
        };
      }
    });

    setPrices((currentPrices) => ({
      ...currentPrices,
      ...fetchedPrices,
    }));
  };

  // Fetch prices immediately on portfolio load or market status change
  useEffect(() => {
    if (!portfolio?.holdings) return;

    const cancelledRef = { current: false };
    fetchPricesForHoldings(portfolio.holdings, cancelledRef);

    return () => {
      cancelledRef.current = true;
    };
  }, [portfolio, marketOpen]);

  // Auto-refresh prices only when market is open
  useEffect(() => {
    if (!portfolio?.holdings || !marketOpen) return;

    const cancelledRef = { current: false };
    const interval = setInterval(() => {
      fetchPricesForHoldings(portfolio.holdings, cancelledRef);
    }, 10_000);

    return () => {
      cancelledRef.current = true;
      clearInterval(interval);
    };
  }, [portfolio, marketOpen]);

  // Show loading state until portfolio loads
  if (!portfolio) {
    return <p className="p-6 text-slate-500">Loading portfolio...</p>;
  }

  // Render dashboard components
  return (
    <main className="p-6 grid grid-cols-1 gap-6">
      
      {/* AI AUTO-PILOT DASHBOARD */}
      <div className={`trading-card rounded-2xl p-6 transition-all duration-500 border ${isBotEnabled ? 'border-sky-500 shadow-[0_0_20px_-5px_rgba(14,165,233,0.3)]' : 'border-slate-200 dark:border-slate-800'}`}>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
                {isBotEnabled ? (
                  <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-sky-500"></span>
                  </span>
                ) : (
                  <span className="h-3 w-3 rounded-full bg-slate-300 dark:bg-slate-700"></span>
                )}
                AI Auto-Trader (Sleep Mode)
              </h2>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              When enabled, the AI will automatically scan the market and execute trades on your behalf.
            </p>
          </div>
          
          <div className="flex items-center gap-4 w-full md:w-auto">
            <div className="flex-1 md:flex-none md:w-48">
              <select 
                className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-sm font-semibold text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500 disabled:opacity-50"
                value={botStrategyId}
                onChange={handleStrategyChange}
                disabled={isBotEnabled}
              >
                {strategies.map((strat: any) => (
                  <option key={strat.id} value={strat.id}>
                    {strat.name}
                  </option>
                ))}
              </select>
            </div>
            
            <button
              onClick={handleToggleBot}
              className={`relative inline-flex h-8 w-14 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 focus-visible:ring-offset-2 ${isBotEnabled ? 'bg-sky-500' : 'bg-slate-200 dark:bg-slate-700'}`}
              role="switch"
              aria-checked={isBotEnabled}
            >
              <span className="sr-only">Toggle AI Bot</span>
              <span
                className={`pointer-events-none inline-block h-7 w-7 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${isBotEnabled ? 'translate-x-6' : 'translate-x-0'}`}
              />
            </button>
          </div>
        </div>
      </div>

      <PortfolioSummary
        portfolio={portfolio}
        performance={portfolioPerformance}
      />
      <PortfolioHoldingsTable
        holdings={portfolio.holdings}
        prices={prices}
      />
      <TradeHistoryTable trades={portfolio.trade_history} />
    </main>
  );
}
