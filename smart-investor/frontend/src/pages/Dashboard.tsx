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

  const [error, setError] = useState<string | null>(null);

  // Load portfolio and bot data on initial render
  useEffect(() => {
    Promise.all([
      fetchPortfolio(),
      fetchStrategies(),
      fetchBotStatus()
    ]).then(([portRes, stratRes, botRes]) => {
      setPortfolio(portRes.data);
      setStrategies(stratRes.data.strategies);
      setIsBotEnabled(botRes.data.is_bot_enabled);
      setBotStrategyId(botRes.data.bot_strategy_id);
    }).catch((err) => {
      console.error("Dashboard load failed", err);
      setError("Failed to load your portfolio. The server might be unreachable or rate limited (429). Please try refreshing.");
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

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4 text-red-500">
          {error}
        </div>
      </div>
    );
  }

  // Show loading state until portfolio loads
  if (!portfolio) {
    return <p className="p-6 text-slate-500">Loading portfolio...</p>;
  }

  // Render dashboard components
  return (
    <main className="p-6 grid grid-cols-1 gap-6">
      
      {/* AI AUTO-PILOT DASHBOARD */}
      <div className={`relative overflow-hidden rounded-2xl p-4 md:p-5 transition-all duration-500 border ${isBotEnabled ? 'border-sky-500/50 bg-sky-500/5 shadow-[0_0_30px_-10px_rgba(14,165,233,0.3)]' : 'border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900'}`}>
        {isBotEnabled && (
          <div className="absolute top-0 right-0 h-full w-1/2 bg-gradient-to-l from-sky-500/10 to-transparent pointer-events-none" />
        )}
        <div className="flex flex-col xl:flex-row items-start xl:items-center justify-between gap-5 relative z-10">
          <div className="flex items-start gap-4">
            <div className={`mt-1 flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${isBotEnabled ? 'bg-sky-500 shadow-[0_0_15px_rgba(14,165,233,0.5)]' : 'bg-slate-100 dark:bg-slate-800'}`}>
              <svg xmlns="http://www.w3.org/2000/svg" className={`h-5 w-5 ${isBotEnabled ? 'text-white' : 'text-slate-400'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base md:text-lg font-black text-slate-900 dark:text-white tracking-tight">
                  AI Autonomous Agent
                </h2>
                {isBotEnabled && (
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-sky-500/10 px-2 py-0.5 text-[10px] font-bold text-sky-500 tracking-wider">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-sky-500"></span>
                    </span>
                    ACTIVE
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-md leading-relaxed">
                Sleep mode enabled. AI will monitor the market and execute live trades based on your selected strategy parameters.
              </p>
            </div>
          </div>
          
          <div className="flex flex-row items-center justify-between xl:justify-end gap-3 w-full xl:w-auto mt-2 xl:mt-0 pt-4 xl:pt-0 border-t xl:border-t-0 border-slate-100 dark:border-slate-800/50">
            <div className="flex-1 xl:flex-none">
              <select 
                className={`w-full xl:w-56 appearance-none bg-slate-50 dark:bg-slate-950/50 border ${isBotEnabled ? 'border-sky-500/30 text-sky-700 dark:text-sky-400' : 'border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300'} rounded-xl p-2.5 px-3 text-xs font-bold focus:outline-none focus:ring-2 focus:ring-sky-500 disabled:opacity-60 transition-colors`}
                value={botStrategyId}
                onChange={handleStrategyChange}
                disabled={isBotEnabled}
              >
                {strategies.map((strat: any) => (
                  <option key={strat.id} value={strat.id}>
                    {strat.name.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>
            
            <button
              onClick={handleToggleBot}
              className={`relative inline-flex h-9 w-16 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-all duration-300 ease-in-out focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 focus-visible:ring-offset-2 ${isBotEnabled ? 'bg-sky-500 shadow-inner' : 'bg-slate-200 dark:bg-slate-700'}`}
              role="switch"
              aria-checked={isBotEnabled}
            >
              <span className="sr-only">Toggle AI Bot</span>
              <span
                className={`pointer-events-none flex h-7 w-7 transform items-center justify-center rounded-full bg-white shadow-md ring-0 transition duration-300 ease-in-out ${isBotEnabled ? 'translate-x-7' : 'translate-x-0'}`}
              >
                {isBotEnabled && (
                  <svg className="h-4 w-4 text-sky-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </span>
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
