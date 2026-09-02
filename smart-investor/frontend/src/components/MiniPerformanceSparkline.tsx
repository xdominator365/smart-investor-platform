interface MiniPerformanceSparklineProps {
  values: number[];
  positive: boolean;
}

export default function MiniPerformanceSparkline({
  values,
  positive,
}: MiniPerformanceSparklineProps) {
  if (!values.length) return null;

  const width = 120;
  const height = 42;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const points = values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = height - ((value - min) / range) * (height - 8) - 4;
      return `${x},${y}`;
    })
    .join(" ");

  const stroke = positive ? "#34d399" : "#f87171";
  const fill = positive ? "rgba(52, 211, 153, 0.18)" : "rgba(248, 113, 113, 0.18)";

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="h-10 w-[120px]"
      aria-label="Performance mini chart"
      role="img"
    >
      <defs>
        <linearGradient id={`spark-${positive ? 'green' : 'red'}`} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={fill} />
          <stop offset="100%" stopColor="rgba(15, 23, 42, 0)" />
        </linearGradient>
      </defs>
      <polyline
        points={points}
        fill="none"
        stroke={stroke}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <polyline
        points={`0,${height} ${points} ${width},${height}`}
        fill={`url(#spark-${positive ? 'green' : 'red'})`}
        opacity="0.9"
      />
    </svg>
  );
}
