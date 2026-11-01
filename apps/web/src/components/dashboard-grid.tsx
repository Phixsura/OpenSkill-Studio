"use client";

interface Widget { widgetId: string; title: string; widgetType: string; data: Record<string, unknown>; }

export function DashboardGrid({ widgets, onRemove }: { widgets: Widget[]; onRemove?: (id: string) => void }) {
  if (!widgets.length) return <div className="text-center text-gray-400 py-8 text-sm">Add widgets to your dashboard</div>;
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {widgets.map(w => (
        <div key={w.widgetId} className="border dark:border-gray-700 rounded-xl p-4 relative group">
          <button onClick={() => onRemove?.(w.widgetId)}
            className="absolute top-2 right-2 text-xs text-gray-300 opacity-0 group-hover:opacity-100">✕</button>
          <span className="text-xs text-gray-500 uppercase">{w.widgetType}</span>
          <h4 className="font-bold text-sm mt-0.5">{w.title}</h4>
          {w.widgetType === "counter" && <span className="text-2xl font-extrabold block mt-1">{String(w.data.value ?? 0)}</span>}
          {w.widgetType === "status" && (
            <span className={`text-sm font-medium mt-1 block ${w.data.status === "operational" ? "text-green-600" : "text-red-600"}`}>
              {w.data.status === "operational" ? "✅ Operational" : "⚠️ Issues"}
            </span>
          )}
          {w.widgetType === "chart" && <div className="h-16 bg-gray-50 dark:bg-gray-800 rounded mt-2 flex items-center justify-center text-xs text-gray-400">Chart placeholder</div>}
        </div>
      ))}
    </div>
  );
}
