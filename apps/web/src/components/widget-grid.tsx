"use client";

interface Widget { id: string; title: string; icon: string; size: string; type: string; }
interface WidgetGridProps { widgets: Widget[]; onRemove: (id: string) => void; }

const SIZE_CLASS: Record<string, string> = { sm: "col-span-1", md: "col-span-2", lg: "col-span-3" };

export function WidgetGrid({ widgets, onRemove }: WidgetGridProps) {
  return (
    <div className="grid grid-cols-4 gap-3">
      {widgets.map(w => (
        <div key={w.id} className={`${SIZE_CLASS[w.size] || "col-span-1"} rounded-xl border dark:border-gray-700 p-4`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <span>{w.icon}</span>
              <span className="text-sm font-medium">{w.title}</span>
            </div>
            <button onClick={() => onRemove(w.id)} className="text-xs text-gray-300 hover:text-red-500">×</button>
          </div>
          <div className="h-16 bg-gray-50 dark:bg-gray-800 rounded flex items-center justify-center text-xs text-gray-400">
            {w.type} widget
          </div>
        </div>
      ))}
    </div>
  );
}
