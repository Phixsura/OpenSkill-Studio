"use client";

interface RequestInfo { request_id: string; method: string; path: string; status_code: number; duration_ms: number; saved: boolean; }
interface Props { requests: RequestInfo[]; stats: { total: number; saved: number; errors: number }; appName: string; }

const mColor: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600", PATCH: "text-orange-600" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiPlaygroundCard({ requests, stats, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">▶️ API Playground</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{stats.total} requests · {stats.saved} saved</span>
      </div>
      {requests.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No playground requests</p>
      ) : (
        <div className="space-y-1">
          {requests.map((r) => (
            <div key={r.request_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`font-mono font-bold ${mColor[r.method] ?? "text-gray-500"}`}>{r.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.path}</span>
                {r.saved && <span className="text-[9px] text-yellow-500">★</span>}
              </div>
              <span className={`font-mono ${r.status_code >= 400 ? "text-red-500" : "text-gray-400"}`}>{r.status_code} · {r.duration_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
