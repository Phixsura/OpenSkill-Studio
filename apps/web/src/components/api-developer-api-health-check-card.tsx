"use client";

interface CheckResult { check_name: string; status: string; message: string; duration_ms: number; }
interface Props { checks: CheckResult[]; allPassing: boolean; appName: string; }

const sDot: Record<string, string> = { pass: "bg-green-500", fail: "bg-red-500", warn: "bg-yellow-500" };

export default function APIDeveloperAPIHealthCheckCard({ checks, allPassing, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏥 Health Checks</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`rounded px-2 py-0.5 text-[11px] font-medium ${allPassing ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" : "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"}`}>
          {allPassing ? "All passing" : "Issues detected"}
        </span>
      </div>
      {checks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No health checks</p>
      ) : (
        <div className="space-y-1">
          {checks.map((c) => (
            <div key={c.check_name} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${sDot[c.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{c.check_name}</span>
              </div>
              <span className="text-gray-400">{c.duration_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
