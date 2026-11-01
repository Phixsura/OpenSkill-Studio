"use client";

interface CohortInfo { cohort_month: string; initial_count: number; retention_1m: number; retention_3m: number; retention_12m: number; health: string; }
interface Props { cohorts: CohortInfo[]; avgRetention3m: number; appName: string; }

const hColor: Record<string, string> = { excellent: "text-green-600", good: "text-blue-600", fair: "text-yellow-600", poor: "text-red-600" };

export default function APIDeveloperPlatformSDKApiDeveloperApiApiPlatformDeveloperRetentionCard({ cohorts, avgRetention3m, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Developer Retention</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-blue-600">{avgRetention3m}% 3m avg</span>
      </div>
      {cohorts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No retention data</p>
      ) : (
        <div className="space-y-2">
          {cohorts.map((c) => (
            <div key={c.cohort_month} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{c.cohort_month} ({c.initial_count})</span>
                <span className={hColor[c.health] ?? ""}>{c.health}</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>1m: {c.retention_1m}%</span>
                <span>3m: {c.retention_3m}%</span>
                <span>12m: {c.retention_12m}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
