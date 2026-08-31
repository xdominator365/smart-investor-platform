import MiniPerformanceSparkline from "./MiniPerformanceSparkline";

interface PortfolioPerformance {
  return_1d: number;
  return_5d: number;
  return_30d: number;
}

interface PortfolioSummaryProps {
  portfolio: any;
  performance?: PortfolioPerformance;
}

const buildSparkline = (value: number) => {
  const absValue = Math.max(Math.abs(value), 0.5);
  const direction = value >= 0 ? 1 : -1;

  return Array.from({ length: 7 }, (_, index) => {
    const wave = Math.sin(index * 1.2 + 1.2) * 7;
    const drift = absValue * (0.8 + index * 0.18);
    const base = 36 + index * 5 + wave;
    return value >= 0 ? base + drift : base - drift * 0.8 + (direction * 6);
  });
};

export default function PortfolioSummary({
  portfolio,
  performance,
}: PortfolioSummaryProps) {
  const return1d = performance?.return_1d ?? 0;
  const return5d = performance?.return_5d ?? 0;
  const return30d = performance?.return_30d ?? 0;

  const cards = [
    {
      label: "Cash",
      value: `₹ ${portfolio.cash_balance}`,
      accent: "from-sky-500/20 to-blue-600/10 text-sky-600 dark:text-sky-300",
      glow: "shadow-[0_18px_50px_-24px_rgba(59,130,246,0.7)]",
      sparkline: buildSparkline(return1d || 0.8),
      positive: return1d >= 0,
    },
    {
      label: "Realized P&L",
      value: `₹ ${portfolio.realized_pnl}`,
      accent: "from-emerald-500/20 to-green-600/10 text-emerald-600 dark:text-emerald-300",
      glow: "shadow-[0_18px_50px_-24px_rgba(16,185,129,0.7)]",
      sparkline: buildSparkline(return1d || 1.2),
      positive: return1d >= 0,
    },
    {
      label: "Unrealized P&L",
      value: `₹ ${portfolio.unrealized_pnl}`,
      accent: "from-amber-500/20 to-yellow-600/10 text-amber-600 dark:text-amber-300",
      glow: "shadow-[0_18px_50px_-24px_rgba(245,158,11,0.7)]",
      sparkline: buildSparkline(return5d || -0.6),
      positive: return5d >= 0,
    },
    {
      label: "Total P&L",
      value: `₹ ${portfolio.total_pnl}`,
      accent: "from-violet-500/20 to-fuchsia-600/10 text-violet-600 dark:text-violet-300",
      glow: "shadow-[0_18px_50px_-24px_rgba(168,85,247,0.75)]",
      sparkline: buildSparkline(return30d || 2.4),
      positive: return30d >= 0,
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
