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
  return (
    <div className="rounded-2xl bg-card p-6 shadow-lg border border-slate-200 dark:border-slate-700">
      <h2 className="text-sm uppercase tracking-wide text-mutedText mb-2">
        AI Signal
      </h2>

      <p
        className={`text-5xl font-extrabold ${
          signal === "BUY"
            ? "text-green-500"
            : signal === "SELL"
            ? "text-red-500"
            : "text-yellow-400"
        }`}
      >
        {signal}
      </p>

      <div className="mt-4">
        <div className="flex justify-between text-xs mb-1">
          <span>Confidence</span>
          <span>{confidence}%</span>
        </div>
        <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
          <div
            className="bg-sky-500 h-2 rounded-full transition-all"
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      <p className="mt-4 text-sm text-slate-600 dark:text-slate-300">
        {reason}
      </p>
    </div>
  );
}
