interface TradeHistoryTableProps {
  trades: any[];
}

export default function TradeHistoryTable({ trades }: TradeHistoryTableProps) {
  if (!trades || trades.length === 0) {
    return (
      <div className="col-span-1 md:col-span-2 rounded-xl bg-white dark:bg-slate-800 p-6 shadow">
        <p className="text-sm text-slate-500">No trades executed yet.</p>
      </div>
    );
  }

  return (
    <div className="col-span-1 md:col-span-2 rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-lg border border-slate-200 dark:border-slate-700">
      <h2 className="text-sm uppercase tracking-wide text-slate-500 mb-4">
        Trade History
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b">
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
                  className="border-b last:border-none dark:border-slate-700"
                >
                  <td className="py-2">
                    {new Date(t.time).toLocaleString()}
                  </td>
                  <td>{t.symbol}</td>
                  <td
                    className={
                      t.side === "BUY"
                        ? "text-green-500"
                        : "text-red-500"
                    }
                  >
                    {t.side}
                  </td>
                  <td>{t.quantity}</td>
                  <td>₹ {t.price}</td>
                  <td
                    className={
                      t.pnl >= 0
                        ? "text-green-500"
                        : "text-red-500"
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
