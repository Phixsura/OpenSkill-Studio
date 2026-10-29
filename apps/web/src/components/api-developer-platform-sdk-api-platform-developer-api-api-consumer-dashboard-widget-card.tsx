"use client";

interface WidgetInfo { widget_id: string; widget_type: string; title: string; data_source: string; width: number; }
interface Props { dashboardTitle: string; widgets: WidgetInfo[]; consumerId: string; appName: string; }

const typeIcon: Record<string, string> = { chart: "📊", counter: "🔢", table: "📋", status: "🟢", timeline: "📅", gauge: "🎯", heatmap: "🗺️" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDashboardWidgetCard({ dashboardTitle, widgets, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📱 {dashboardTitle}</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {widgets.length} widgets</p>
      </div>
      {widgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No widgets configured</p>
      ) : (
        <div className="grid grid-cols-2 gap-1.5">
          {widgets.map((w) => (
            <div key={w.widget_id} className="rounded bg-gray-50 p-1.5 text-center text-[10px] dark:bg-gray-800">
              <div>{typeIcon[w.widget_type] ?? "•"}</div>
              <div className="font-medium text-gray-700 dark:text-gray-300">{w.title}</div>
              <div className="text-gray-400">{w.data_source}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
