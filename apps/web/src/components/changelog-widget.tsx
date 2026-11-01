"use client";

interface ChangeItem { version: string; title: string; type: string; date: string; }
interface ChangelogWidgetProps { items: ChangeItem[]; hasMore: boolean;
  onViewAll: () => void; }

const TYPE_BADGE: Record<string, { emoji: string; color: string }> = {
  added: { emoji: "✨", color: "bg-green-100 text-green-700" },
  fixed: { emoji: "🐛", color: "bg-orange-100 text-orange-700" },
  changed: { emoji: "🔄", color: "bg-blue-100 text-blue-700" },
};

export function ChangelogWidget({ items, hasMore, onViewAll }: ChangelogWidgetProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden w-72">
      <div className="p-3 border-b dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <h4 className="text-sm font-semibold">📋 What&apos;s New</h4>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {items.map((item, i) => {
          const badge = TYPE_BADGE[item.type] || { emoji: "📌", color: "bg-gray-100" };
          return (
            <div key={i} className="px-3 py-2">
              <div className="flex items-center gap-1.5 mb-0.5">
                <span className={`text-xs px-1 rounded ${badge.color}`}>{badge.emoji} {item.type}</span>
                <span className="text-xs text-gray-400">v{item.version}</span>
              </div>
              <p className="text-sm">{item.title}</p>
            </div>
          );
        })}
      </div>
      {hasMore && (
        <button onClick={onViewAll} className="w-full py-2 text-xs text-blue-600 hover:bg-gray-50 dark:hover:bg-gray-800 border-t dark:border-gray-700">
          View all changes →
        </button>
      )}
    </div>
  );
}
