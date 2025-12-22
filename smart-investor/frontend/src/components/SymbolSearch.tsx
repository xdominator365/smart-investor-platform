interface SymbolSearchProps {
  symbol: string;
  setSymbol: (value: string) => void;
  onFetch: () => void;
}

export default function SymbolSearch({
  symbol,
  setSymbol,
  onFetch,
}: SymbolSearchProps) {
  return (
    <div className="p-6 flex gap-3">
      <input
        value={symbol}
        onChange={(e) => setSymbol(e.target.value)}
        className="px-3 py-2 rounded border dark:bg-slate-800"
        placeholder="TCS.NS"
      />
      <button
        onClick={onFetch}
        className="px-4 py-2 bg-sky-500 text-white rounded hover:bg-sky-600"
      >
        Fetch
      </button>
    </div>
  );
}
