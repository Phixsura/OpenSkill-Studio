"use client";

interface Request { id: string; name: string; method: string; path: string; }
interface Collection { id: string; name: string; requests: Request[]; }
interface HistoryItem { requestId: string; status: number; latencyMs: number; executedAt: string; }
interface Props { collections: Collection[]; history: HistoryItem[]; consumerId: string; appName: string; }

const methodColors: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-amber-600", DELETE: "text-red-600" };

export default function APIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiPlaygroundV2Card({ collections, history, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎮 API Playground V2</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {collections.length} collections</p>
      </div>
      {collections.length > 0 && (
        <div className="mb-3 space-y-2">
          {collections.slice(0, 3).map((c) => (
            <div key={c.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="text-[11px] font-medium text-gray-700 dark:text-gray-300">{c.name}</div>
              <div className="mt-0.5 space-y-0.5">
                {c.requests.slice(0, 3).map((r) => (
                  <div key={r.id} className="flex gap-1 text-[10px]">
                    <span className={`font-bold ${methodColors[r.method] ?? "text-gray-500"}`}>{r.method}</span>
                    <code className="text-gray-500">{r.path}</code>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
      {history.length > 0 && (
        <div>
          <div className="text-[10px] text-gray-400 mb-1">Recent:</div>
          {history.slice(0, 3).map((h) => (
            <div key={h.requestId} className="flex justify-between text-[9px] text-gray-500">
              <span className={h.status < 400 ? "text-green-500" : "text-red-500"}>{h.status}</span>
              <span>{h.latencyMs}ms · {h.executedAt}</span>
            </div>
          ))}
        </div>
      )}
      {collections.length === 0 && history.length === 0 && <p className="text-center text-sm text-gray-400">Start exploring the API</p>}
    </div>
  );
}
