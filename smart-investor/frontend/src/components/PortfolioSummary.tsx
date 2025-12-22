interface PortfolioSummaryProps {
  portfolio: any;
}

export default function PortfolioSummary({ portfolio }: PortfolioSummaryProps) {
  return (
    <div className="col-span-1 md:col-span-2 grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow">
        <p className="text-sm text-slate-500">Cash</p>
        <p className="text-xl font-bold">₹ {portfolio.cash_balance}</p>
      </div>

      <div className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow">
        <p className="text-sm text-slate-500">Realized P&L</p>
        <p className="text-xl font-bold text-green-500">
          ₹ {portfolio.realized_pnl}
        </p>
      </div>

      <div className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow">
        <p className="text-sm text-slate-500">Unrealized P&L</p>
        <p className="text-xl font-bold text-yellow-400">
          ₹ {portfolio.unrealized_pnl}
        </p>
      </div>

      <div className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow">
        <p className="text-sm text-slate-500">Total P&L</p>
        <p className="text-xl font-bold text-sky-500">
          ₹ {portfolio.total_pnl}
        </p>
      </div>
    </div>
  );
}
