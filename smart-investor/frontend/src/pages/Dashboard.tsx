import { useEffect, useState } from "react";
import {
  fetchPortfolio,
  fetchStock,
  fetchMarketStatusAPI,
} from "../api";

import PortfolioSummary from "../components/PortfolioSummary";
import PortfolioHoldingsTable from "../components/PortfolioHoldingsTable";
import TradeHistoryTable from "../components/TradeHistoryTable";

export default function Dashboard() {
  const [portfolio, setPortfolio] = useState<any>(null);
  const [prices, setPrices] = useState<Record<string, {
    current_price: number;
    return_1d: number;
    return_5d: number;
    return_30d: number;
  }>>({});
  const [marketOpen, setMarketOpen] = useState(false);

  // Load portfolio on initial render
  useEffect(() => {
    fetchPortfolio().then((res) => setPortfolio(res.data));
  }, []);

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

    const priceMap: Record<string, {
      current_price: number;
      return_1d: number;
      return_5d: number;
      return_30d: number;
    }> = {};

    results.forEach(([symbol, stockData]) => {
      if (stockData && typeof stockData.current_price === "number") {
        priceMap[symbol] = {
          current_price: stockData.current_price,
          return_1d: Number(stockData.return_1d ?? 0),
          return_5d: Number(stockData.return_5d ?? 0),
          return_30d: Number(stockData.return_30d ?? 0),
        };
      }
    });

    setPrices(priceMap);
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
      <PortfolioSummary portfolio={portfolio} />
      <PortfolioHoldingsTable
        holdings={portfolio.holdings}
        prices={prices}
      />
      <TradeHistoryTable trades={portfolio.trade_history} />
    </main>
  );
}
