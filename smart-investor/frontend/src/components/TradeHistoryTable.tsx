interface TradeHistoryTableProps {
  trades: any[];
}

export default function TradeHistoryTable({ trades }: TradeHistoryTableProps) {
  if (!trades || trades.length === 0) {
    return (
      <div className="trading-card col-span-1 md:col-span-2">
        <p className="text-sm text-slate-500 dark:text-slate-400">No trades executed yet.</p>
      </div>
    );
  }

  return (
    <div className="trading-card col-span-1 md:col-span-2">
      <h2 className="mb-4 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
        Trade History
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-slate-500 dark:border-slate-700 dark:text-slate-400">
              <th className="py-2">Time</th>
              <th>Symbol</th>
              <th>Side</th>
              <th>Qty</th>
              <th>Price</th>
              <th>P&L</th>
            </tr>
          </thead>

          <tbody>
            {trades
              .slice()
              .reverse()
              .map((t, i) => (
                <tr
                  key={i}
                  className="border-b border-slate-200 last:border-none dark:border-slate-700"
                >
                  <td className="py-2 text-slate-600 dark:text-slate-200">
                    {new Date(t.time).toLocaleString()}
                  </td>
                  <td className="text-slate-700 dark:text-slate-100">{t.symbol}</td>
                  <td
                    className={
                      t.side === "BUY"
                        ? "font-bold text-emerald-500"
                        : "font-bold text-rose-500"
                    }
                  >
                    {t.side}
                  </td>
                  <td className="text-slate-700 dark:text-slate-200">{t.quantity}</td>
                  <td className="text-slate-700 dark:text-slate-200">₹ {t.price}</td>
                  <td
                    className={
                      t.pnl >= 0
                        ? "font-bold text-emerald-500"
                        : "font-bold text-rose-500"
                    }
                  >
                    {t.pnl !== undefined ? `₹ ${t.pnl}` : "-"}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
