interface StockCardProps {
  price: number;
  symbol: string;
}

export default function StockCard({ price, symbol }: StockCardProps) {
  return (
    <div className="rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-lg border border-slate-200 dark:border-slate-700">
      <h2 className="text-sm uppercase tracking-wide text-slate-500 mb-2">
        Stock Snapshot
      </h2>
      <p className="text-4xl font-bold">₹ {price}</p>
      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{symbol}</p>
    </div>
  );
}
