interface HeaderProps {
  theme: "dark" | "light";
  onToggleTheme: () => void;
}

export default function Header({ theme, onToggleTheme }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-slate-300 dark:border-slate-700">
      <h1 className="text-xl font-semibold text-sky-500">
        GenZ Investor
      </h1>
      <button
        onClick={onToggleTheme}
        className="px-3 py-1 rounded bg-sky-500 text-white hover:bg-sky-600"
      >
        {theme === "dark" ? "Light Mode" : "Dark Mode"}
      </button>
    </header>
  );
}
