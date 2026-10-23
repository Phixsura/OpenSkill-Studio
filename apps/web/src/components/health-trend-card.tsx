"use client";

interface Trend { metric: string; trend: string; change_pct?: number; }
interface HealthTrendCardProps { trends: Trend[]; overall: string; needsAttention: boolean; }

const TREND_ICONS: Record<string, string> = { improving: "📈", degrading: "📉", stable: "➡️" };
const TREND_COLORS: Record<string, string> = { improving: "text-green-600", degrading: "text-red-600", stable: "text-gray-500" };

export function HealthTrendCard({ trends, overall, needsAttention }: HealthTrendCardProps) {
  return (
    <div className={`rounded-lg border p-4 ${needsAttention ? "border-red-200 dark:border-red-800" : "border-gray-200 dark:border-gray-700"}`}>
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Health Trends</h3>
        <span className={`text-sm font-medium ${TREND_COLORS[overall] || ""}`}>
          {TREND_ICONS[overall] || "➡️"} {overall}
        </span>
      </div>
      <ul className="mt-3 space-y-1">
        {trends.map(t => (
          <li key={t.metric} className="flex items-center justify-between text-sm">
            <span>{t.metric}</span>
            <span className={TREND_COLORS[t.trend] || ""}>
              {TREND_ICONS[t.trend]} {t.change_pct != null ? `${t.change_pct}%` : t.trend}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
