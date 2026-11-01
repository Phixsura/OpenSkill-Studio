"use client";

interface Route { id: string; method: string; pattern: string; status: number; enabled: boolean; callCount: number; }
interface Props { routes: Route[]; consumerId: string; appName: string; }

const methodColors: Record<string, string> = {
  GET: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  POST: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  PUT: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  DELETE: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiMockServerCard({ routes, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎭 Mock Server</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {routes.length} routes</p>
      </div>
      {routes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No mock routes</p>
      ) : (
        <div className="space-y-1">
          {routes.map((r) => (
            <div key={r.id} className={`flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800 ${!r.enabled ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1">
                <span className={`rounded px-1 py-0.5 text-[9px] font-bold ${methodColors[r.method] ?? "bg-gray-200 text-gray-600"}`}>{r.method}</span>
                <code className="text-gray-600 dark:text-gray-400">{r.pattern}</code>
              </div>
              <div className="flex gap-2 text-gray-400">
                <span>{r.status}</span>
                <span>{r.callCount} calls</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
