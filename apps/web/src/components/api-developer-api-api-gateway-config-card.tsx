"use client";

interface RouteInfo { route_id: string; path_pattern: string; upstream: string; methods: string[]; rate_limit: number | null; auth_required: boolean; enabled: boolean; timeout_ms: number; }
interface Props { routes: RouteInfo[]; appName: string; }

export default function APIDeveloperAPIApiGatewayConfigCard({ routes, appName }: Props) {
  const enabledCount = routes.filter(r => r.enabled).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚪 API Gateway</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{enabledCount}/{routes.length} enabled</span>
      </div>
      {routes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No gateway routes</p>
      ) : (
        <div className="space-y-2">
          {routes.map((r) => (
            <div key={r.route_id} className={`rounded-lg px-3 py-2 ${r.enabled ? "bg-gray-50 dark:bg-gray-800" : "bg-gray-100 opacity-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{r.path_pattern}</span>
                <span className="text-[9px] text-gray-400">{r.methods.join(", ")}</span>
              </div>
              <div className="mt-0.5 flex gap-2 text-[10px] text-gray-400">
                <span>→ {r.upstream}</span>
                {r.rate_limit && <span>{r.rate_limit} rpm</span>}
                {r.auth_required && <span>🔒</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
