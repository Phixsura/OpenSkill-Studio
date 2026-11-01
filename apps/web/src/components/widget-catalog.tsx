"use client";

interface Widget { id: string; name: string; category: string; preview: string; }
interface WidgetCatalogProps { widgets: Widget[]; onSelect: (id: string) => void; }

export function WidgetCatalog({ widgets, onSelect }: WidgetCatalogProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Widget Library</h3>
      <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
        {widgets.map(w => (
          <button key={w.id} onClick={() => onSelect(w.id)}
            className="rounded-lg border border-gray-200 p-3 text-center transition hover:border-blue-400 dark:border-gray-700">
            <span className="text-2xl">{w.preview}</span>
            <p className="mt-1 text-xs font-medium">{w.name}</p>
            <p className="text-xs text-gray-400">{w.category}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
