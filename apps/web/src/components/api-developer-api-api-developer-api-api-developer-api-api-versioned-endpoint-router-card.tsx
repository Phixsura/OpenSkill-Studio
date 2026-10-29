"use client";

interface RouteInfo { endpoint: string; versions: Record<string, string>; default_version: string; request_counts: Record<string, number>; }
interface Props { routes: RouteInfo[]; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiVersionedEndpointRouterCard({ routes, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔀 Versioned Router</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {routes.length} endpoints</p>
      </div>
      {routes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No versioned routes</p>
      ) : (
        <div className="space-y-2">
          {routes.map((r) => (
            <div key={r.endpoint} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <span className="text-[11px] font-medium text-gray-700 dark:text-gray-300">{r.endpoint}</span>
              <div className="mt-1 flex gap-1">
                {Object.entries(r.versions).map(([v]) => (
                  <span key={v} className={`rounded px-1.5 py-0.5 text-[9px] ${v === r.default_version ? "bg-green-100 text-green-700 font-bold" : "bg-gray-100 text-gray-600"}`}>{v}: {r.request_counts[v] ?? 0}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
