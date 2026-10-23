"use client";

interface Widget { widget_id: string; type: string; title: string;
  type_info: { icon: string; label: string }; position: { x: number; y: number; w: number; h: number }; }
interface DashboardWidgetGridProps { widgets: Widget[]; columns: number;
  onRemove: (id: string) => void; onAdd: () => void; }

export function DashboardWidgetGrid({ widgets, columns, onRemove, onAdd }: DashboardWidgetGridProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Dashboard</h2>
        <button onClick={onAdd} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Add Widget</button>
      </div>
      <div className="grid gap-3" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
        {widgets.map(w => (
          <div key={w.widget_id} className="rounded-lg border p-3 dark:border-gray-700"
            style={{ gridColumn: `span ${w.position.w}`, gridRow: `span ${w.position.h}` }}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <span>{w.type_info.icon}</span>
                <span className="text-sm font-medium">{w.title}</span>
              </div>
              <button onClick={() => onRemove(w.widget_id)} className="text-xs text-red-400">×</button>
            </div>
            <p className="mt-1 text-xs text-gray-400">{w.type_info.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
