"use client";

interface Entry { id: string; method: string; path: string; status: number; latencyMs: number; timestamp: string; }
interface Props { entries: Entry[]; totalMatches: number; query: string; consumerId: string; appName: string; }

const methodColors: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-amber-600", DELETE: "text-red-600" };

export default function APIDeveloperPlatformSDKConsumerApiRequestLogSearchCard({ entries, totalMatches, query, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔎 Log Search</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}{query ? ` · "${query}" (${totalMatches} results)` : ""}</p>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">{query ? "No results found" : "Search request logs"}</p>
      ) : (
        <div className="space-y-0.5">
          {entries.slice(0, 10).map((e) => (
            <div key={e.id} className="flex items-center justify-between text-[10px]">
              <div className="flex items-center gap-1">
                <span className={`font-bold ${methodColors[e.method] ?? "text-gray-500"}`}>{e.method}</span>
                <code className="text-gray-600 dark:text-gray-400">{e.path}</code>
              </div>
              <div className="flex gap-2">
                <span className={e.status < 400 ? "text-green-500" : "text-red-500"}>{e.status}</span>
                <span className="text-gray-400">{e.latencyMs}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
