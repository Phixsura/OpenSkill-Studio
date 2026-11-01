"use client";

interface LogInfo { log_id: string; method: string; path: string; status_code: number; duration_ms: number; consumer_id: string; }
interface Props { logs: LogInfo[]; totalCount: number; errorCount: number; appName: string; }

const mColor: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600" };

export default function APIDeveloperAPIApiDeveloperApiRequestLoggerCard({ logs, totalCount, errorCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Request Logger</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalCount.toLocaleString()} logs</p>
        </div>
        {errorCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{errorCount} errors</span>}
      </div>
      {logs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No request logs</p>
      ) : (
        <div className="space-y-1">
          {logs.map((l) => (
            <div key={l.log_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`font-mono font-bold ${mColor[l.method] ?? "text-gray-500"}`}>{l.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{l.path}</span>
              </div>
              <span className={`font-mono ${l.status_code >= 400 ? "text-red-500" : "text-gray-400"}`}>{l.status_code} · {l.duration_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
