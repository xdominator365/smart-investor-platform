interface Holding {
  symbol: string;
  quantity: number;
  avg_price: number;
}

interface StockSnapshot {
  current_price: number;
  return_1d: number;
  return_5d: number;
  return_30d: number;
}

interface PortfolioHoldingsProps {
  holdings: Holding[];
  prices: Record<string, StockSnapshot>;
}

const formatReturn = (value: number) => {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
};

const returnClass = (value: number) =>
  `transition-colors duration-300 ${
    value >= 0 ? "text-green-500" : "text-red-500"
  }`;

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

  // Calculate totals for Qty, Invested, Current Value, and P&L
  let totalQty = 0;
  let totalInvested = 0;
  let totalCurrentValue = 0;
  let totalPnL = 0;
  let weightedReturn1d = 0;
  let weightedReturn5d = 0;
  let weightedReturn30d = 0;

  holdings.forEach((h) => {
    const stockData =
      prices[h.symbol] ?? {
        current_price: h.avg_price,
        return_1d: 0,
        return_5d: 0,
        return_30d: 0,
      };
    const currentPrice = stockData.current_price;
    const invested = h.quantity * h.avg_price;
    const currentValue = h.quantity * currentPrice;
    const pnl = currentValue - invested;
    totalQty += h.quantity;
    totalInvested += invested;
    totalCurrentValue += currentValue;
    totalPnL += pnl;
    weightedReturn1d += stockData.return_1d * invested;
    weightedReturn5d += stockData.return_5d * invested;
    weightedReturn30d += stockData.return_30d * invested;
  });

  const totalReturn1d = totalInvested ? weightedReturn1d / totalInvested : 0;
  const totalReturn5d = totalInvested ? weightedReturn5d / totalInvested : 0;
  const totalReturn30d = totalInvested ? weightedReturn30d / totalInvested : 0;

  return (
    <div className="col-span-1 md:col-span-2 rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-lg border border-slate-200 dark:border-slate-700">
      <h2 className="mb-4 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
        Portfolio Holdings
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-slate-500 dark:border-slate-700 dark:text-slate-400">
              <th className="py-2">Symbol</th>
              <th>Qty</th>
              <th>Avg Price</th>
              <th>Current Price</th>
              <th>Invested</th>
              <th>Current Value</th>
              <th>P&L</th>
              <th>1D %</th>
              <th>5D %</th>
              <th>30D %</th>
            </tr>
          </thead>

          <tbody>
            {holdings.map((h, i) => {
              const stockData =
                prices[h.symbol] ?? {
                  current_price: h.avg_price,
                  return_1d: 0,
                  return_5d: 0,
                  return_30d: 0,
                };
              const currentPrice = stockData.current_price;
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
                  <td className={returnClass(pnl)}>
                    ₹ {pnl.toFixed(2)}
                  </td>
                  <td className={returnClass(stockData.return_1d)}>
                    {formatReturn(stockData.return_1d)}
                  </td>
                  <td className={returnClass(stockData.return_5d)}>
                    {formatReturn(stockData.return_5d)}
                  </td>
                  <td className={returnClass(stockData.return_30d)}>
                    {formatReturn(stockData.return_30d)}
                  </td>
                </tr>
              );
            })}
            {/* Total row */}
            <tr className="border-t border-slate-200 bg-slate-100 font-bold dark:border-slate-700 dark:bg-slate-900">
              <td className="py-2">Total</td>
              <td>{totalQty}</td>
              <td></td>
              <td></td>
              <td>₹ {totalInvested.toFixed(2)}</td>
              <td>₹ {totalCurrentValue.toFixed(2)}</td>
              <td className={returnClass(totalPnL)}>₹ {totalPnL.toFixed(2)}</td>
              <td className={`${returnClass(totalReturn1d)} whitespace-nowrap`}>
                {formatReturn(totalReturn1d)}
              </td>
              <td className={`${returnClass(totalReturn5d)} whitespace-nowrap`}>
                {formatReturn(totalReturn5d)}
              </td>
              <td className={`${returnClass(totalReturn30d)} whitespace-nowrap`}>
                {formatReturn(totalReturn30d)}
              </td>
            </tr>

            <tr className="border-t border-slate-200 bg-slate-50 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:border-slate-700 dark:bg-slate-900/80 dark:text-slate-400">
              <td className="py-2">Total 1D / 5D / 30D</td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td className={`${returnClass(totalReturn1d)} whitespace-nowrap`}>
                {formatReturn(totalReturn1d)}
              </td>
              <td className={`${returnClass(totalReturn5d)} whitespace-nowrap`}>
                {formatReturn(totalReturn5d)}
              </td>
              <td className={`${returnClass(totalReturn30d)} whitespace-nowrap`}>
                {formatReturn(totalReturn30d)}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
