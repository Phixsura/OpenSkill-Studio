"use client";

interface WarningInfo { endpoint: string; method: string; replacement: string; sunset_date: string; consumers_warned_count: number; total_warnings_sent: number; }
interface Props { warnings: WarningInfo[]; appName: string; }

export default function APIDeveloperAPIApiEndpointDeprecationWarningCard({ warnings, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚠️ Deprecation Warnings</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {warnings.length} deprecated</p>
      </div>
      {warnings.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No deprecation warnings</p>
      ) : (
        <div className="space-y-2">
          {warnings.map((w) => (
            <div key={`${w.method}-${w.endpoint}`} className="rounded-lg bg-yellow-50 p-2 dark:bg-yellow-900/20">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{w.method} {w.endpoint}</span>
                <span className="text-[10px] text-yellow-600">sunset: {w.sunset_date}</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>→ {w.replacement}</span>
                <span>{w.consumers_warned_count} consumers · {w.total_warnings_sent} warnings</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
