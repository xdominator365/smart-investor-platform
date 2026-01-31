type Props = {
  insight: any;
};

// Helper function to format time ago

function timeAgo(isoTime?: string) {
  if (!isoTime) return "Unknown";

  const diffMs = Date.now() - new Date(isoTime).getTime();
  const mins = Math.floor(diffMs / 60000);

  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins} min ago`;

  const hours = Math.floor(mins / 60);
  return `${hours} hr ago`;
}

export default function NewsInsightCard({ insight }: Props) {
  if (!insight || insight.status === "NO_DATA") {
    return (
      <div className="p-4 rounded-xl border bg-slate-50 dark:bg-slate-900">
        <h3 className="font-semibold text-lg mb-2">📰 News Intelligence</h3>
        <p className="text-slate-500 text-sm">
          No recent news available for this stock.
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 rounded-xl border bg-white dark:bg-slate-900 shadow-sm">
      <h3 className="font-semibold text-lg mb-3">📰 News Insights</h3>
      
      <p className="text-xs text-slate-500 mb-3">
      Last updated: {timeAgo(insight.last_updated_at)}
      </p>

      <div className="space-y-1 text-sm">
        <p>
          <strong>Sentiment:</strong>{" "}
          <span
            className={
              insight.sentiment.label === "POSITIVE"
                ? "text-green-600"
                : insight.sentiment.label === "NEGATIVE"
                ? "text-red-600"
                : "text-yellow-600"
            }
          >
            {insight.sentiment.label}
          </span>
        </p>

        <p>
          <strong>Trend:</strong> {insight.sentiment.trend}
        </p>

        <p>
          <strong>Attention:</strong>{" "}
          {insight.attention.attention_level}
        </p>

        {insight.risk_flags?.length > 0 && (
          <p className="text-red-500 font-medium">
            ⚠ {insight.risk_flags.join(", ")}
          </p>
        )}
      </div>

      <p className="mt-3 text-xs italic text-slate-500">
        {insight.summary}
      </p>
    </div>
  );
}