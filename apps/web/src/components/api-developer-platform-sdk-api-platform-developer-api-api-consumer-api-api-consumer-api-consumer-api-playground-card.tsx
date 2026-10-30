"use client";

interface HistoryItem { id: string; method: string; path: string; status: number; durationMs: number; }
interface Props { history: HistoryItem[]; savedCount: number; consumerId: string; appName: string; }

const methodColors: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-amber-600", PATCH: "text-purple-600", DELETE: "text-red-600",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPlaygroundCard({ history, savedCount, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎮 API Playground</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {savedCount} saved requests</p>
      </div>
      {history.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No recent requests</p>
      ) : (
        <div className="space-y-1">
          {history.slice(0, 8).map((h) => (
            <div key={h.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <div className="flex items-center gap-1">
                <span className={`font-bold ${methodColors[h.method] ?? "text-gray-500"}`}>{h.method}</span>
                <code className="text-gray-600 dark:text-gray-400">{h.path}</code>
              </div>
              <div className="flex gap-2">
                <span className={h.status < 400 ? "text-green-500" : "text-red-500"}>{h.status}</span>
                <span className="text-gray-400">{h.durationMs}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
