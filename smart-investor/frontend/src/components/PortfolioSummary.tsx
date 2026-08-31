import MiniPerformanceSparkline from "./MiniPerformanceSparkline";

interface PortfolioSummaryProps {
  portfolio: any;
}

export default function PortfolioSummary({ portfolio }: PortfolioSummaryProps) {
  const cards = [
    {
      label: "Cash",
      value: `₹ ${portfolio.cash_balance}`,
      accent: "from-sky-500/20 to-blue-600/10 text-sky-600 dark:text-sky-300",
      glow: "shadow-[0_18px_50px_-24px_rgba(59,130,246,0.7)]",
      sparkline: [38, 41, 39, 45, 49, 52, 58],
      positive: true,
    },
    {
      label: "Realized P&L",
      value: `₹ ${portfolio.realized_pnl}`,
      accent: "from-emerald-500/20 to-green-600/10 text-emerald-600 dark:text-emerald-300",
      glow: "shadow-[0_18px_50px_-24px_rgba(16,185,129,0.7)]",
      sparkline: [20, 24, 28, 31, 35, 38, 45],
      positive: true,
    },
    {
      label: "Unrealized P&L",
      value: `₹ ${portfolio.unrealized_pnl}`,
      accent: "from-amber-500/20 to-yellow-600/10 text-amber-600 dark:text-amber-300",
      glow: "shadow-[0_18px_50px_-24px_rgba(245,158,11,0.7)]",
      sparkline: [48, 46, 44, 42, 40, 36, 33],
      positive: false,
    },
    {
      label: "Total P&L",
      value: `₹ ${portfolio.total_pnl}`,
      accent: "from-violet-500/20 to-fuchsia-600/10 text-violet-600 dark:text-violet-300",
      glow: "shadow-[0_18px_50px_-24px_rgba(168,85,247,0.75)]",
      sparkline: [30, 35, 32, 36, 45, 49, 54],
      positive: true,
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className={`trading-card relative overflow-hidden ${card.glow}`}
        >
          <div className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${card.accent}`} />
          <div className="flex items-center justify-between">
            <p className="metric-label">{card.label}</p>
            <span className={`h-2.5 w-2.5 rounded-full bg-gradient-to-br ${card.accent.replace('/20', '').replace('/10', '')}`} />
          </div>
          <div className="mt-3 flex items-end justify-between gap-3">
            <p className="metric-value text-[1.35rem] md:text-[1.6rem]">
              {card.value}
            </p>
            <MiniPerformanceSparkline
              values={card.sparkline}
              positive={card.positive}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
