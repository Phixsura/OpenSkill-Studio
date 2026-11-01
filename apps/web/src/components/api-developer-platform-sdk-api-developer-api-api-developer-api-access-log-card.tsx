"use client";

interface EntryInfo { entry_id: string; consumer_id: string; method: string; path: string; status_code: number; latency_ms: number; }
interface Props { entries: EntryInfo[]; totalCount: number; errorCount: number; appName: string; }

const mColor: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600" };

export default function APIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiAccessLogCard({ entries, totalCount, errorCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Access Log</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalCount.toLocaleString()} entries</p>
        </div>
        {errorCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{errorCount} errors</span>}
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No access logs</p>
      ) : (
        <div className="space-y-1">
          {entries.slice(0, 8).map((e) => (
            <div key={e.entry_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`font-mono font-bold ${mColor[e.method] ?? "text-gray-500"}`}>{e.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{e.path}</span>
              </div>
              <span className={`font-mono ${e.status_code >= 400 ? "text-red-500" : "text-gray-400"}`}>{e.status_code} · {e.latency_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
