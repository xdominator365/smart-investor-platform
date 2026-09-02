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
    <div className="trading-card col-span-1 md:col-span-2">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
          Paper Trading
        </h2>
        <span className="rounded-full bg-emerald-500/10 px-2 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-emerald-600 dark:text-emerald-300">
          Live
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <label className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200">
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">Qty</span>
          <input
            type="number"
            min={1}
            value={quantity}
            onChange={(e) => setQuantity(Number(e.target.value))}
            className="w-20 border-0 bg-transparent text-right text-base font-bold text-slate-900 outline-none dark:text-white"
          />
        </label>

        <button
          onClick={onBuy}
          className="rounded-xl bg-gradient-to-r from-emerald-500 to-green-600 px-5 py-2.5 text-sm font-bold text-white shadow-[0_20px_28px_-18px_rgba(16,185,129,0.9)] transition hover:scale-[1.01]"
        >
          Buy
        </button>

        <button
          onClick={onSell}
          className="rounded-xl bg-gradient-to-r from-rose-500 to-red-600 px-5 py-2.5 text-sm font-bold text-white shadow-[0_20px_28px_-18px_rgba(239,68,68,0.9)] transition hover:scale-[1.01]"
        >
          Sell
        </button>

        <button
          onClick={onAutoTrade}
          className="rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 px-5 py-2.5 text-sm font-bold text-white shadow-[0_20px_28px_-18px_rgba(37,99,235,0.9)] transition hover:scale-[1.01]"
        >
          Auto Trade
        </button>
      </div>

      {message && (
        <p className="mt-4 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200">
          {message}
        </p>
      )}
    </div>
  );
}
