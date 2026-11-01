"use client";

interface ErrorInfo { error_code: string; category: string; count: number; endpoints_affected_count: number; }
interface Props { errors: ErrorInfo[]; totalErrors: number; categoryBreakdown: Record<string, number>; appName: string; }

const catColor: Record<string, string> = { auth: "text-yellow-600", rate_limit: "text-orange-600", validation: "text-blue-600", timeout: "text-purple-600", client: "text-gray-600", server: "text-red-600" };

export default function APIDeveloperAPIApiErrorClassificationCard({ errors, totalErrors, categoryBreakdown, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏷️ Error Classification</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-red-500">{totalErrors.toLocaleString()}</span>
      </div>
      <div className="mb-3 flex flex-wrap gap-2">
        {Object.entries(categoryBreakdown).map(([cat, count]) => (
          <span key={cat} className={`text-[10px] font-medium ${catColor[cat] ?? "text-gray-500"}`}>{cat}: {count}</span>
        ))}
      </div>
      {errors.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No errors</p>
      ) : (
        <div className="space-y-1">
          {errors.map((e) => (
            <div key={e.error_code} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{e.error_code}</span>
              <span className="text-gray-400">{e.count}× · {e.endpoints_affected_count} endpoints</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
