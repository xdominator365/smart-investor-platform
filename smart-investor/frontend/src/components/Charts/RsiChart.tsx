import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface RsiChartProps {
  data: any[];
}

export default function RsiChart({ data }: RsiChartProps) {
  return (
    <div className="rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-lg border border-slate-200 dark:border-slate-700">
      <h2 className="text-sm uppercase tracking-wide text-slate-500 mb-4">
        RSI
      </h2>

      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <XAxis dataKey="date" hide />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Line type="monotone" dataKey="rsi" stroke="#A855F7" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
