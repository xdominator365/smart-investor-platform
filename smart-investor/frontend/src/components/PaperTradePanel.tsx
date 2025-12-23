interface PaperTradePanelProps {
  quantity: number;
  setQuantity: (q: number) => void;
  onBuy: () => void;
  onSell: () => void;
  onAutoTrade: () => void;
  message: string;
  marketOpen: boolean;
}

export default function PaperTradePanel({
  quantity,
  setQuantity,
  onBuy,
  onSell,
  onAutoTrade,
  message,
}: PaperTradePanelProps) {
  return (
    <div className="col-span-1 md:col-span-2 rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-lg border border-slate-200 dark:border-slate-700">
      <h2 className="text-sm uppercase tracking-wide text-slate-500 mb-4">
        Paper Trading
      </h2>

      <div className="flex flex-wrap items-center gap-4">
        <input
          type="number"
          min={1}
          value={quantity}
          onChange={(e) => setQuantity(Number(e.target.value))}
          className="w-24 px-3 py-2 rounded border dark:bg-slate-700"
        />

        <button
          onClick={onBuy}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Buy
        </button>

        <button
          onClick={onSell}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Sell
        </button>

        <button
          onClick={onAutoTrade}
          className="px-4 py-2 bg-sky-500 text-white rounded hover:bg-sky-600"
        >
          Auto Trade
        </button>
      </div>

      {message && (
        <p className="mt-4 text-sm text-slate-500">{message}</p>
      )}
    </div>
  );
}
