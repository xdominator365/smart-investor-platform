interface Decision {
  time: string;
  signal: string;
  rsi: number;
  ma20: number;
  ma50: number;
  action: string;
  reason: string;
}

interface Props {
  decisions: Decision[];
}

export default function AutoTradeExplainability({ decisions }: Props) {
  if (!decisions.length) {
    return (
      <div className="rounded-xl bg-white dark:bg-slate-800 p-6 shadow">
        <p className="text-slate-500">No auto-trade decisions yet.</p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-lg border border-slate-200 dark:border-slate-700">
      <h2 className="text-sm uppercase tracking-wide text-slate-500 mb-4">
        Auto-Trade Decision Log
      </h2>

      <div className="space-y-4 max-h-80 overflow-y-auto">
        {decisions.map((d, i) => (
          <div
            key={i}
            className="p-4 rounded-lg border dark:border-slate-700"
          >
            <div className="flex justify-between text-xs text-slate-500">
              <span>{new Date(d.time).toLocaleString()}</span>
              <span
                className={
                  d.action.includes("EXECUTED")
                    ? "text-green-500"
                    : d.action.includes("BLOCKED")
                    ? "text-red-500"
                    : "text-yellow-400"
                }
              >
                {d.action}
              </span>
            </div>

            <p className="mt-2 font-semibold">
              Signal: {d.signal}
            </p>

            <p className="text-sm text-slate-600 dark:text-slate-300">
              RSI: {d.rsi.toFixed(2)} | MA20: {d.ma20.toFixed(2)} | MA50: {d.ma50.toFixed(2)}
            </p>

            <p className="text-xs mt-1 text-slate-500">
              Reason: {d.reason}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
