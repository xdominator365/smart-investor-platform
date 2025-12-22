interface Holding {
  symbol: string;
  quantity: number;
  avg_price: number;
}

interface PortfolioHoldingsProps {
  holdings: Holding[];
  prices: Record<string, number>;
}

export default function PortfolioHoldingsTable({
  holdings,
  prices,
}: PortfolioHoldingsProps) {
  if (!holdings || holdings.length === 0) {
    return (
      <div className="col-span-1 md:col-span-2 rounded-xl bg-white dark:bg-slate-800 p-6 shadow">
        <p className="text-sm text-slate-500">No holdings yet.</p>
      </div>
    );
  }

  return (
    <div className="col-span-1 md:col-span-2 rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-lg border border-slate-200 dark:border-slate-700">
      <h2 className="text-sm uppercase tracking-wide text-slate-500 mb-4">
        Portfolio Holdings
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b">
              <th className="py-2">Symbol</th>
              <th>Qty</th>
              <th>Avg Price</th>
              <th>Current Price</th>
              <th>Invested</th>
              <th>Current Value</th>
              <th>P&L</th>
            </tr>
          </thead>

          <tbody>
            {holdings.map((h, i) => {
              const currentPrice = prices[h.symbol] ?? h.avg_price;
              const invested = h.quantity * h.avg_price;
              const currentValue = h.quantity * currentPrice;
              const pnl = currentValue - invested;

              return (
                <tr
                  key={i}
                  className="border-b last:border-none dark:border-slate-700"
                >
                  <td className="py-2 font-medium">{h.symbol}</td>
                  <td>{h.quantity}</td>
                  <td>₹ {h.avg_price.toFixed(2)}</td>
                  <td>₹ {currentPrice.toFixed(2)}</td>
                  <td>₹ {invested.toFixed(2)}</td>
                  <td>₹ {currentValue.toFixed(2)}</td>
                  <td
                    className={
                      pnl >= 0 ? "text-green-500" : "text-red-500"
                    }
                  >
                    ₹ {pnl.toFixed(2)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
