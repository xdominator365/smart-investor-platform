
import { NavLink } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";
import { useEffect, useState } from "react";
import { fetchMarketStatusAPI, fetchStock } from "../api";

type TickerItem = {
  label: string;
  value: number;
  returnPct: number;
};

export default function Header() {
  const [marketOpen, setMarketOpen] = useState<boolean | null>(null);
  const [tickerData, setTickerData] = useState<TickerItem[]>([]);

  useEffect(() => {
    let isMounted = true;
    const fetchStatus = async () => {
      try {
        const res = await fetchMarketStatusAPI();
        if (isMounted) setMarketOpen(res.data.market_open);
      } catch (e) {
        if (isMounted) setMarketOpen(null);
      }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // 30s
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    const symbols = ["^NSEI", "^BSESN", "RELIANCE.NS", "TCS.NS", "BTC-USD", "GC=F"];

    const loadTicker = async () => {
      try {
        const responses = await Promise.all(
          symbols.map(async (symbol) => {
            try {
              const res = await fetchStock(symbol);
              return {
                label: symbol === "^NSEI" ? "NIFTY 50" : symbol === "^BSESN" ? "SENSEX" : symbol,
                value: Number(res.data.current_price ?? 0),
                returnPct: Number(res.data.return_1d ?? 0),
              };
            } catch {
              return null;
            }
          })
        );

        const valid = responses.filter(Boolean) as TickerItem[];
        if (valid.length) setTickerData(valid);
      } catch {}
    };

    loadTicker();
    const interval = setInterval(loadTicker, 45000);
    return () => clearInterval(interval);
  }, []);

  const marketTicker = tickerData.length
    ? tickerData
    : [
        { label: "NIFTY 50", value: 0, returnPct: 1.24 },
        { label: "SENSEX", value: 0, returnPct: 0.96 },
        { label: "RELIANCE", value: 0, returnPct: -0.42 },
        { label: "TCS", value: 0, returnPct: 1.88 },
        { label: "BTC/USD", value: 0, returnPct: -1.1 },
        { label: "GOLD", value: 0, returnPct: 0.33 },
      ];

  // Market status badge
  const MarketStatusBadge = () => (
    <span
      className={`ml-4 flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold shadow-sm select-none
        ${marketOpen === null ? "bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-300" :
          marketOpen ? "bg-green-100 text-green-700 border border-green-300 dark:bg-green-900 dark:text-green-200" :
          "bg-red-100 text-red-700 border border-red-300 dark:bg-red-900 dark:text-red-200"}
      `}
      title={marketOpen === null ? "Status unavailable" : marketOpen ? "Market is open" : "Market is closed"}
    >
      <span className={`inline-block w-2 h-2 rounded-full mr-1
        ${marketOpen === null ? "bg-gray-400" : marketOpen ? "bg-green-500" : "bg-red-500"}
      `} />
      {marketOpen === null ? "Status..." : marketOpen ? "Market Open" : "Market Closed"}
    </span>
  );

  return (
    <>
      <div className="mb-5 overflow-hidden rounded-2xl border border-cyan-500/20 bg-slate-950/90 px-3 py-2 shadow-[0_0_30px_rgba(34,211,238,0.12)] backdrop-blur-xl">
        <div className="ticker-track flex min-w-full items-center gap-6 whitespace-nowrap text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-300">
          {marketTicker.map((item, index) => (
            <div key={`${item.label}-${index}`} className="flex items-center gap-2">
              <span className="text-cyan-300">{item.label}</span>
              <span className={item.returnPct >= 0 ? "text-emerald-400" : "text-red-400"}>
                {item.returnPct >= 0 ? "+" : ""}
                {item.returnPct.toFixed(2)}%
              </span>
              {index < marketTicker.length - 1 && <span className="text-slate-500">•</span>}
            </div>
          ))}
        </div>
      </div>

      <header className="glass-panel sticky top-4 z-20 flex items-center justify-between gap-4 rounded-[28px] px-4 py-3 md:px-6">
        <div className="flex items-center gap-3 select-none">
          <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 via-sky-500 to-emerald-400 shadow-[0_18px_35px_-18px_rgba(14,165,233,0.9)]">
            <svg width="28" height="28" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-7 w-7">
              <path d="M16 26c-4.5 0-8-2.5-8-6.5 0-2.5 2-4.5 4.5-4.5 1.5 0 2.5 1 3.5 2 1-1 2-2 3.5-2C22 15 24 17 24 19.5c0 4-3.5 6.5-8 6.5z" fill="#ecfeff"/>
              <path d="M16 24c-3.5 0-6-1.8-6-4.5 0-1.7 1.3-3 3-3 1 0 1.7.7 2.5 1.5.8-.8 1.5-1.5 2.5-1.5 1.7 0 3 1.3 3 3 0 2.7-2.5 4.5-6 4.5z" fill="#d1fae5"/>
              <circle cx="16" cy="13" r="2.5" fill="#f8fafc"/>
            </svg>
          </span>

          <div>
            <div className="font-sans text-xl font-black tracking-[-0.06em] text-slate-900 dark:text-white md:text-2xl">
              My Dhira
            </div>
            <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500 dark:text-slate-400">
              Capital Intelligence
            </div>
          </div>
        </div>

        <nav className="flex items-center gap-2 md:gap-3">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `rounded-full px-3 py-2 text-sm font-bold tracking-wide transition-all duration-200 md:px-4 ${
                isActive
                  ? "bg-gradient-to-r from-sky-500 to-blue-600 text-white shadow-[0_20px_30px_-15px_rgba(37,99,235,0.9)]"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
              }`
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/stocks"
            className={({ isActive }) =>
              `rounded-full px-3 py-2 text-sm font-bold tracking-wide transition-all duration-200 md:px-4 ${
                isActive
                  ? "bg-gradient-to-r from-violet-500 to-fuchsia-600 text-white shadow-[0_20px_30px_-15px_rgba(168,85,247,0.8)]"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
              }`
            }
          >
            Stocks
          </NavLink>

          <MarketStatusBadge />
          <ThemeToggle />
        </nav>
      </header>
    </>
  );
}
