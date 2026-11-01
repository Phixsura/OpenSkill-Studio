"use client";

interface ErrorInfo { total_errors: number; unique_error_codes: number; top_error_code: string; top_error_count: number; error_rate_trend: string; most_affected_endpoint: string; }
interface Props { errors: ErrorInfo; appName: string; }

const trendIcon: Record<string, string> = { increasing: "📈", decreasing: "📉", stable: "➡️" };

export default function APIDeveloperAPIErrorAnalyticsCard({ errors: e, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">❌ Error Analytics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-red-500">{e.total_errors.toLocaleString()} errors</span>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        {[
          { l: "Unique Codes", v: e.unique_error_codes },
          { l: "Top Error", v: e.top_error_code || "—" },
          { l: "Top Count", v: e.top_error_count },
          { l: "Trend", v: `${trendIcon[e.error_rate_trend] ?? ""} ${e.error_rate_trend}` },
          { l: "Affected EP", v: e.most_affected_endpoint || "—" },
        ].map((m) => (
          <div key={m.l} className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-[11px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[7px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
