"use client";

interface WebhookEvent { type: string; category: string; description: string; }
interface WebhookEventCatalogProps { events: WebhookEvent[]; categories: string[];
  selectedCategory: string | null; onSelectCategory: (cat: string | null) => void; }

const CAT_ICONS: Record<string, string> = {
  lifecycle: "🔄", user: "👤", billing: "💳", deploy: "🚀",
};

export function WebhookEventCatalog({ events, categories, selectedCategory, onSelectCategory }: WebhookEventCatalogProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📡 Webhook Events</h3>
        <span className="text-xs text-gray-400">{events.length} events</span>
      </div>
      <div className="flex gap-1 px-4 py-2 border-b dark:border-gray-700">
        <button onClick={() => onSelectCategory(null)}
          className={`px-2 py-0.5 text-[10px] rounded ${!selectedCategory ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>All</button>
        {categories.map(c => (
          <button key={c} onClick={() => onSelectCategory(c)}
            className={`px-2 py-0.5 text-[10px] rounded ${selectedCategory === c ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
            {CAT_ICONS[c] ?? ""} {c}
          </button>
        ))}
      </div>
      <div className="divide-y dark:divide-gray-700">
        {events.map(e => (
          <div key={e.type} className="flex items-center justify-between px-4 py-2">
            <span className="text-sm font-mono">{e.type}</span>
            <span className="text-xs text-gray-400">{e.description}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
