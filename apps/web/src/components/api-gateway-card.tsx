"use client";

interface GatewayRouteInfo {
  route_id: string;
  path_prefix: string;
  upstream: string;
  strip_prefix: boolean;
  enabled: boolean;
  request_count: number;
}

interface APIGatewayCardProps {
  routes: GatewayRouteInfo[];
  appName: string;
}

export default function APIGatewayCard({ routes, appName }: APIGatewayCardProps) {
  const enabled = routes.filter((r) => r.enabled).length;
  const totalReqs = routes.reduce((s, r) => s + r.request_count, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌉 API Gateway</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {enabled}/{routes.length} active · {totalReqs} reqs
        </span>
      </div>

      {routes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No gateway routes</p>
      ) : (
        <div className="space-y-1.5">
          {routes.map((r) => (
            <div
              key={r.route_id}
              className={`rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800 ${!r.enabled ? "opacity-50" : ""}`}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                  {r.path_prefix}
                </span>
                <span className="text-[10px] text-gray-400">{r.request_count} reqs</span>
              </div>
              <p className="text-[10px] text-gray-400">→ {r.upstream}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
