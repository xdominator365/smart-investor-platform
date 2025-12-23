import { NavLink } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";

export default function Header() {
  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-slate-300 dark:border-slate-700">

      <div className="flex items-center gap-3 select-none">
        {/*investor icon: lotus/meditation */}
        <span className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-sky-100 to-emerald-100 dark:from-sky-900 dark:to-emerald-900 shadow-inner">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-8 h-8">
            <path d="M16 26c-4.5 0-8-2.5-8-6.5 0-2.5 2-4.5 4.5-4.5 1.5 0 2.5 1 3.5 2 1-1 2-2 3.5-2C22 15 24 17 24 19.5c0 4-3.5 6.5-8 6.5z" fill="#38bdf8"/>
            <path d="M16 24c-3.5 0-6-1.8-6-4.5 0-1.7 1.3-3 3-3 1 0 1.7.7 2.5 1.5.8-.8 1.5-1.5 2.5-1.5 1.7 0 3 1.3 3 3 0 2.7-2.5 4.5-6 4.5z" fill="#34d399"/>
            <circle cx="16" cy="13" r="2.5" fill="#0ea5e9"/>
          </svg>
        </span>
        <span className="font-serif text-3xl font-extrabold tracking-tight text-emerald-700 dark:text-emerald-300 drop-shadow-sm">
          My Dhira
        </span>
        <span className="ml-2 text-xs font-medium italic text-slate-500 dark:text-slate-300 hidden sm:inline-block"></span>
      </div>

      <nav className="flex gap-6 text-base">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `transition-all duration-200 px-5 py-2 rounded-full shadow-md font-bold tracking-wide border-2 ${
              isActive
                ? "bg-gradient-to-r from-sky-400 to-blue-600 text-white border-sky-500 scale-105 shadow-lg"
                : "bg-white/80 dark:bg-slate-800/80 text-sky-600 border-sky-200 hover:bg-sky-100 hover:scale-105 hover:shadow-lg dark:hover:bg-sky-900/80"
            }`
          }
        >
          <span className="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0h6" />
            </svg>
            Dashboard
          </span>
        </NavLink>

        <NavLink
          to="/stocks"
          className={({ isActive }) =>
            `transition-all duration-200 px-5 py-2 rounded-full shadow-md font-bold tracking-wide border-2 ${
              isActive
                ? "bg-gradient-to-r from-pink-400 to-fuchsia-600 text-white border-pink-500 scale-105 shadow-lg"
                : "bg-white/80 dark:bg-slate-800/80 text-pink-600 border-pink-200 hover:bg-pink-100 hover:scale-105 hover:shadow-lg dark:hover:bg-pink-900/80"
            }`
          }
        >
          <span className="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 17v-2a4 4 0 014-4h10a4 4 0 014 4v2M16 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            Stocks
          </span>
        </NavLink>
      {/* Light/Dark mode toggle */}
      <ThemeToggle />
      </nav>
    </header>
  );
}
