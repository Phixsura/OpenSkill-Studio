"use client";

interface MeshRouteInfo {
  source: string;
  destination: string;
  allowed: boolean;
  timeout_ms: number;
  request_count: number;
}

interface ServiceMeshCardProps {
  routes: MeshRouteInfo[];
  appName: string;
}

export default function ServiceMeshCard({ routes, appName }: ServiceMeshCardProps) {
  const blockedCount = routes.filter((r) => !r.allowed).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Service Mesh</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{routes.length} routes</span>
          {blockedCount > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {blockedCount} blocked
            </span>
          )}
        </div>
      </div>

      {routes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No routes configured</p>
      ) : (
        <div className="space-y-1.5">
          {routes.map((r) => (
            <div
              key={`${r.source}-${r.destination}`}
              className={`flex items-center justify-between rounded px-2.5 py-1.5 ${
                r.allowed
                  ? "hover:bg-gray-50 dark:hover:bg-gray-800/50"
                  : "bg-red-50/50 dark:bg-red-950/10"
              }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-2 w-2 rounded-full ${r.allowed ? "bg-green-500" : "bg-red-500"}`}
                />
                <span className="text-xs text-gray-700 dark:text-gray-300">{r.source}</span>
                <span className="text-gray-400">→</span>
                <span className="text-xs text-gray-700 dark:text-gray-300">{r.destination}</span>
              </div>
              <div className="flex items-center gap-3 text-[11px] text-gray-400">
                <span>{r.timeout_ms}ms timeout</span>
                <span>{r.request_count} req</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
