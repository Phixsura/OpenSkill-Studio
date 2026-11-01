"use client";

interface RouteInfo { route_id: string; path_pattern: string; upstream: string; methods: string[]; middlewares: string[]; enabled: boolean; }
interface Props { routes: RouteInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiGatewayConfigCard({ routes, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌐 Gateway Config</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {routes.length} routes</p>
      </div>
      {routes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No routes configured</p>
      ) : (
        <div className="space-y-2">
          {routes.map((r) => (
            <div key={r.route_id} className={`rounded-lg p-2 text-[11px] ${r.enabled ? "bg-gray-50 dark:bg-gray-800" : "bg-gray-50/50 opacity-50 dark:bg-gray-800/50"}`}>
              <div className="flex items-center justify-between">
                <span className="font-mono text-gray-700 dark:text-gray-300">{r.path_pattern}</span>
                <span className={r.enabled ? "text-green-600 dark:text-green-400" : "text-gray-400"}>●</span>
              </div>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {r.middlewares.map((m) => (
                  <span key={m} className="rounded bg-blue-100 px-1 text-[9px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{m}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
