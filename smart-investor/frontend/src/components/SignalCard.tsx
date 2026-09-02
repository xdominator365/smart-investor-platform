interface SignalCardProps {
  signal: string;
  confidence: number;
  reason: string;
}

export default function SignalCard({
  signal,
  confidence,
  reason,
}: SignalCardProps) {
  const signalColor =
    signal === "BUY"
      ? "from-emerald-500 to-green-600"
      : signal === "SELL"
      ? "from-rose-500 to-red-600"
      : "from-amber-400 to-yellow-500";

  return (
    <div className="trading-card">
      <div className="mb-5 flex items-center justify-between">
        <p className="metric-label">AI signal</p>
        <span className="rounded-full bg-slate-100 px-2 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500 dark:bg-slate-800 dark:text-slate-300">
          Model
        </span>
      </div>

      <div className={`inline-flex rounded-2xl bg-gradient-to-r ${signalColor} px-4 py-2 shadow-[0_22px_40px_-20px_rgba(16,185,129,0.8)]`}>
        <p className="text-3xl font-black tracking-[-0.07em] text-white">{signal}</p>
      </div>

      <div className="mt-6">
        <div className="mb-2 flex items-center justify-between text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500 dark:text-slate-400">
          <span>Confidence</span>
          <span>{confidence}%</span>
        </div>
        <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
          <div
            className={`h-full rounded-full bg-gradient-to-r ${signalColor} transition-all duration-500`}
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      <p className="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200">
        {reason}
      </p>
    </div>
  );
}
