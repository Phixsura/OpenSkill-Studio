"use client";

interface WidgetInfo {
  widget_id: string;
  widget_type: string;
  title: string;
  data_source: string;
  refresh_interval: number;
  refresh_count: number;
}

interface APIDashboardWidgetCardProps {
  widgets: WidgetInfo[];
  appName: string;
}

const typeIcon: Record<string, string> = { chart: "📈", metric: "🔢", table: "📋", list: "📄" };

export default function APIDashboardWidgetCard({ widgets, appName }: APIDashboardWidgetCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧩 Dashboard Widgets</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{widgets.length} widgets</span>
      </div>

      {widgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No widgets</p>
      ) : (
        <div className="space-y-1.5">
          {widgets.map((w) => (
            <div key={w.widget_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span>{typeIcon[w.widget_type] ?? "📊"}</span>
                <span className="text-xs text-gray-700 dark:text-gray-300">{w.title}</span>
              </div>
              <span className="text-[10px] text-gray-400">{w.refresh_interval}s · {w.refresh_count} refreshes</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
