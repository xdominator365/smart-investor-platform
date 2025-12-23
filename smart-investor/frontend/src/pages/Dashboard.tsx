import { useEffect, useState } from "react";
import { fetchPortfolio, fetchStock } from "../api";
import PortfolioSummary from "../components/PortfolioSummary";
import PortfolioHoldingsTable from "../components/PortfolioHoldingsTable";
import TradeHistoryTable from "../components/TradeHistoryTable";

export default function Dashboard() {
  const [portfolio, setPortfolio] = useState<any>(null);
  const [prices, setPrices] = useState<Record<string, number>>({});

  useEffect(() => {
    fetchPortfolio().then((res) => setPortfolio(res.data));
  }, []);

  // Fetch current prices for all holdings
  useEffect(() => {
    if (!portfolio || !portfolio.holdings) return;
    const symbols = portfolio.holdings.map((h: any) => h.symbol);
    if (symbols.length === 0) return;

    let cancelled = false;
    Promise.all(
      symbols.map((symbol: string) =>
        fetchStock(symbol)
          .then((res) => [symbol, res.data.current_price] as [string, number])
          .catch(() => [symbol, null])
      )
    ).then((results) => {
      if (cancelled) return;
      const priceMap: Record<string, number> = {};
      results.forEach(([symbol, price]) => {
        if (typeof price === "number") priceMap[symbol] = price;
      });
      setPrices(priceMap);
    });
    return () => {
      cancelled = true;
    };
  }, [portfolio]);

  if (!portfolio) {
    return <p className="p-6 text-slate-500">Loading portfolio...</p>;
  }

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
