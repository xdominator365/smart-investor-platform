interface StockCardProps {
  price: number;
  symbol: string;
  ma20?: number;
  ma50?: number;
}

export default function StockCard({ price, symbol, ma20, ma50 }: StockCardProps) {
  const trend =
    typeof ma20 !== "number" || typeof ma50 !== "number"
      ? "Unavailable"
      : ma20 > ma50
      ? "Bullish"
      : ma20 < ma50
      ? "Bearish"
      : "Neutral";
  const trendColor =
    trend === "Bullish"
      ? "text-emerald-500"
      : trend === "Bearish"
      ? "text-red-500"
      : "text-amber-500";

  return (
    <div className="trading-card overflow-hidden">
      <div className="flex items-center justify-between">
        <p className="metric-label">Stock snapshot</p>
        <span className="rounded-full bg-emerald-500/10 px-2 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-emerald-600 dark:text-emerald-300">
          NSE
        </span>
      </div>

      <div className="mt-5 flex items-end justify-between gap-3">
        <div>
          <p className="text-4xl font-black tracking-[-0.06em] text-slate-900 dark:text-white">₹ {price}</p>
          <p className="mt-2 text-sm font-medium text-slate-500 dark:text-slate-400">{symbol}</p>
        </div>
        <div className="rounded-2xl bg-gradient-to-br from-emerald-500/15 to-sky-500/15 px-3 py-2 text-right">
          <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Trend</div>
          <div className={`mt-1 text-sm font-extrabold ${trendColor}`}>{trend}</div>
        </div>
      </div>
    </div>
  );
}
