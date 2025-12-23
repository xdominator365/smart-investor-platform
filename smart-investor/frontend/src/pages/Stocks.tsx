import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Stocks() {
  const [symbol, setSymbol] = useState("");
  const navigate = useNavigate();

  const handleSearch = () => {
    if (!symbol.trim()) return;
    const url = `/stocks/${symbol.toUpperCase()}`;
    window.open(url, '_blank');
  };

  return (
    <main className="p-6">
      <h2 className="text-xl font-semibold mb-4">Search Stock</h2>

      <div className="flex gap-3">
        <input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          placeholder="Enter stock symbol (e.g. RELIANCE.NS)"
          className="px-3 py-2 border rounded dark:bg-slate-800 min-w-[260px] w-full max-w-xs"
        />
        <button
          onClick={handleSearch}
          className="px-4 py-2 bg-sky-500 text-white rounded"
        >
          Search
        </button>
      </div>

      <p className="mt-6 text-slate-500">
        Enter a stock symbol to view charts, signals, and trading options.
      </p>
    </main>
  );
}
