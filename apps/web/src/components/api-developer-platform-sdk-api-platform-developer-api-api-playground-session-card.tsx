"use client";

interface RequestInfo { request_id: string; method: string; path: string; response_status: number; duration_ms: number; }
interface Props { sessionId: string; environment: string; requests: RequestInfo[]; developerName: string; appName: string; }

const methodColor: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlaygroundSessionCard({ sessionId, environment, requests, developerName, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎮 API Playground</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {developerName}</p>
        </div>
        <span className="rounded bg-purple-100 px-1.5 py-0.5 text-[9px] font-medium text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">{environment}</span>
      </div>
      {requests.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No requests yet</p>
      ) : (
        <div className="space-y-1">
          {requests.map((r) => (
            <div key={r.request_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`font-mono font-medium ${methodColor[r.method] ?? "text-gray-600"}`}>{r.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.path}</span>
              </div>
              <span className={r.response_status < 400 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}>{r.response_status} · {Math.round(r.duration_ms)}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
