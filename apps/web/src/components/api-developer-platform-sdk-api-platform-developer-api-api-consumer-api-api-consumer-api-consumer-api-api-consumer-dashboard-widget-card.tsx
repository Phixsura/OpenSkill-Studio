"use client";

interface Widget { id: string; type: string; title: string; width: number; visible: boolean; }
interface Props { widgets: Widget[]; consumerId: string; layout: string; appName: string; }

const typeIcons: Record<string, string> = { metric: "📊", chart: "📈", table: "📋", status: "🔵", alert: "🔔", log: "📜", heatmap: "🗓️" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerDashboardWidgetCard({ widgets, consumerId, layout, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎛️ Dashboard Widgets</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {layout} layout · {widgets.length} widgets</p>
      </div>
      {widgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No widgets</p>
      ) : (
        <div className="space-y-1">
          {widgets.map((w) => (
            <div key={w.id} className={`flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800 ${!w.visible ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1">
                <span>{typeIcons[w.type] ?? "📌"}</span>
                <span className="text-gray-700 dark:text-gray-300">{w.title}</span>
              </div>
              <span className="text-[10px] text-gray-400">{w.width}col</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
