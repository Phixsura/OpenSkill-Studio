"use client";

interface SummaryInfo { developer_id: string; total_requests: number; unique_endpoints: number; error_rate_pct: number; activity_level: string; }
interface Props { summaries: SummaryInfo[]; activityBreakdown: Record<string, number>; appName: string; }

const lvColor: Record<string, string> = { power: "text-purple-600", active: "text-green-600", moderate: "text-blue-600", light: "text-yellow-600", inactive: "text-gray-400" };

export default function APIDeveloperAPIApiDeveloperApiUsageSummaryCard({ summaries, activityBreakdown, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👤 Developer Usage</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {summaries.length} developers</p>
      </div>
      <div className="mb-3 flex flex-wrap gap-2">
        {Object.entries(activityBreakdown).map(([level, count]) => (
          <span key={level} className={`text-[10px] font-medium ${lvColor[level] ?? ""}`}>{level}: {count}</span>
        ))}
      </div>
      {summaries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No developer data</p>
      ) : (
        <div className="space-y-1">
          {summaries.slice(0, 5).map((s) => (
            <div key={s.developer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.developer_id}</span>
              <div className="flex gap-2">
                <span className="text-gray-400">{s.total_requests.toLocaleString()} reqs</span>
                <span className={lvColor[s.activity_level] ?? ""}>{s.activity_level}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
