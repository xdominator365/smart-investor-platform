import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface PriceChartProps {
  data: any[];
}

export default function PriceChart({ data }: PriceChartProps) {
  return (
    <div className="col-span-1 md:col-span-2 rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-lg border border-slate-200 dark:border-slate-700">
      <h2 className="text-sm uppercase tracking-wide text-slate-500 mb-4">
        Price & Moving Averages
      </h2>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <XAxis dataKey="date" hide />
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Line type="monotone" dataKey="price" stroke="#38BDF8" dot={false} />
          <Line type="monotone" dataKey="ma20" stroke="#22C55E" dot={false} />
          <Line type="monotone" dataKey="ma50" stroke="#EF4444" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
