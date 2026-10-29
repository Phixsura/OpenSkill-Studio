"use client";

interface RouteInfo { source: string; destination: string; protocol: string; request_count: number; error_rate: number; latency_ms: number; }
interface Props { routes: RouteInfo[]; unhealthyCount: number; appName: string; }

const pBadge: Record<string, string> = { https: "bg-green-100 text-green-700", grpc: "bg-blue-100 text-blue-700", http2: "bg-purple-100 text-purple-700" };

export default function APIDeveloperPlatformSDKApiDeveloperApiApiPlatformServiceMeshCard({ routes, unhealthyCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🕸️ Service Mesh</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {routes.length} routes</p>
        </div>
        {unhealthyCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{unhealthyCount} unhealthy</span>}
      </div>
      {routes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No service routes</p>
      ) : (
        <div className="space-y-1.5">
          {routes.slice(0, 6).map((r, i) => (
            <div key={i} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1">
                <span className="text-gray-700 dark:text-gray-300">{r.source}</span>
                <span className="text-gray-400">→</span>
                <span className="text-gray-700 dark:text-gray-300">{r.destination}</span>
                <span className={`rounded px-1 py-0.5 text-[8px] ${pBadge[r.protocol] ?? ""}`}>{r.protocol}</span>
              </div>
              <span className={r.error_rate > 5 ? "text-red-500" : "text-gray-400"}>{r.error_rate}% err · {r.latency_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
