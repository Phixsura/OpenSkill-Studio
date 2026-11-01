"use client";

interface RecordInfo { correlation_id: string; origin_service: string; hops: string[]; hop_count: number; completed: boolean; }
interface Props { records: RecordInfo[]; activeCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiRequestCorrelationIdCard({ records, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔗 Correlation IDs</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {activeCount > 0 && <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] text-blue-700">{activeCount} active</span>}
      </div>
      {records.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No correlations</p>
      ) : (
        <div className="space-y-2">
          {records.map((r) => (
            <div key={r.correlation_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-mono text-gray-700 dark:text-gray-300">{r.correlation_id}</span>
                <span className={r.completed ? "text-green-600" : "text-blue-500"}>{r.completed ? "✓" : "⏳"} {r.hop_count} hops</span>
              </div>
              <div className="mt-0.5 flex gap-1 flex-wrap">
                {r.hops.map((h, i) => (
                  <span key={i} className="text-[9px] text-blue-600">{h}{i < r.hops.length - 1 ? " →" : ""}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
