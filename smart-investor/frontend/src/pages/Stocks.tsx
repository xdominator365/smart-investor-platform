import { useState } from "react";

export default function Stocks() {
  const [symbol, setSymbol] = useState("");

  const handleSearch = () => {
    const normalizedSymbol = symbol.trim().toUpperCase();
    if (!normalizedSymbol) return;
    const url = `/stocks/${normalizedSymbol}`;
    window.open(url, "_blank");
  };

  return (
    <main className="px-4 pb-8 pt-2 md:px-6">
      <section className="relative overflow-hidden rounded-3xl border border-cyan-500/20 bg-slate-950 px-5 py-8 shadow-[0_25px_80px_-30px_rgba(8,145,178,0.55)] md:px-10 md:py-12">
        <div className="pointer-events-none absolute -right-16 -top-20 h-56 w-56 rounded-full border border-cyan-400/10 bg-cyan-400/5 blur-2xl" />
        <div className="relative max-w-3xl">
          <div className="mb-5 flex items-center gap-3 text-[10px] font-bold uppercase tracking-[0.28em] text-cyan-300">
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400 shadow-[0_0_14px_rgba(74,222,128,0.9)]" />
            Market scanner
          </div>
          <h2 className="text-3xl font-black tracking-tight text-white md:text-5xl">
            Search Stock
          </h2>
          <p className="mt-3 max-w-xl text-sm leading-6 text-slate-400 md:text-base">
            Pull up live charts, technical signals, and paper-trading controls for any supported symbol.
          </p>

          <form
            className="mt-8 flex flex-col gap-3 sm:flex-row"
            onSubmit={(event) => {
              event.preventDefault();
              handleSearch();
            }}
          >
            <label className="sr-only" htmlFor="stock-symbol">
              Stock symbol
            </label>
            <div className="flex min-h-14 flex-1 items-center rounded-xl border border-slate-700 bg-slate-900/90 px-4 shadow-inner shadow-black/20 transition-colors focus-within:border-cyan-400/70 focus-within:ring-2 focus-within:ring-cyan-400/10">
              <span className="mr-3 text-sm font-bold text-cyan-400">$</span>
              <input
                id="stock-symbol"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                placeholder="RELIANCE.NS"
                autoComplete="off"
                className="w-full bg-transparent text-sm font-semibold uppercase tracking-[0.12em] text-white outline-none placeholder:text-slate-600"
              />
            </div>
            <button
              type="submit"
              disabled={!symbol.trim()}
              className="min-h-14 rounded-xl bg-cyan-400 px-7 text-sm font-black uppercase tracking-[0.16em] text-slate-950 shadow-[0_0_24px_rgba(34,211,238,0.2)] transition-all hover:bg-cyan-300 hover:shadow-[0_0_32px_rgba(34,211,238,0.42)] disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
            >
              Search
            </button>
          </form>

          <div className="mt-6 flex flex-wrap gap-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500">
            <span className="rounded-full border border-slate-800 bg-slate-900/80 px-3 py-1.5">Charts</span>
            <span className="rounded-full border border-slate-800 bg-slate-900/80 px-3 py-1.5">Signals</span>
            <span className="rounded-full border border-slate-800 bg-slate-900/80 px-3 py-1.5">Paper trade</span>
          </div>
        </div>
      </section>
    </main>
  );
}
