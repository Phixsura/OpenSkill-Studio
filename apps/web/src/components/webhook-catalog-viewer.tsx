"use client";

interface EventInfo { type: string; description: string; category: string; fields: string[]; }
interface WebhookCatalogViewerProps { events: EventInfo[]; categories: string[];
  selectedCategory: string | null; onSelectCategory: (cat: string | null) => void; }

export function WebhookCatalogViewer({ events, categories, selectedCategory, onSelectCategory }: WebhookCatalogViewerProps) {
  const filtered = selectedCategory ? events.filter(e => e.category === selectedCategory) : events;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold mb-2">📡 Webhook Events</h3>
        <div className="flex gap-1 flex-wrap">
          <button onClick={() => onSelectCategory(null)}
            className={`text-xs px-2 py-1 rounded ${!selectedCategory ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>All</button>
          {categories.map(c => (
            <button key={c} onClick={() => onSelectCategory(c)}
              className={`text-xs px-2 py-1 rounded capitalize ${selectedCategory === c ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{c}</button>
          ))}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {filtered.map(e => (
          <div key={e.type} className="px-4 py-3">
            <div className="flex items-center gap-2 mb-1">
              <code className="text-sm font-bold text-blue-600 dark:text-blue-400">{e.type}</code>
              <span className="text-xs px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded capitalize">{e.category}</span>
            </div>
            <p className="text-xs text-gray-500">{e.description}</p>
            {e.fields.length > 0 && (
              <div className="flex gap-1 mt-1">
                {e.fields.map(f => <span key={f} className="text-xs font-mono bg-gray-50 dark:bg-gray-800 px-1 rounded">{f}</span>)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
