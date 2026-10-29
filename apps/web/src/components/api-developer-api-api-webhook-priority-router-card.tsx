"use client";

interface RouteInfo { route_id: string; event_type: string; priority: string; destination: string; delivered_count: number; }
interface Props { routes: RouteInfo[]; appName: string; }

const pColor: Record<string, string> = { critical: "bg-red-100 text-red-700", high: "bg-orange-100 text-orange-700", normal: "bg-blue-100 text-blue-700", low: "bg-gray-100 text-gray-600" };

export default function APIDeveloperAPIApiWebhookPriorityRouterCard({ routes, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Priority Router</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {routes.length} routes</p>
      </div>
      {routes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No priority routes</p>
      ) : (
        <div className="space-y-1.5">
          {routes.map((r) => (
            <div key={r.route_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`rounded px-1 py-0.5 text-[9px] font-medium ${pColor[r.priority] ?? ""}`}>{r.priority}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.event_type}</span>
              </div>
              <span className="text-gray-400">{r.delivered_count} delivered</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
