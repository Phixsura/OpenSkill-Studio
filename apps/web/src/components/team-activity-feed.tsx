"use client";

interface FeedItem { user: string; type: string; message: string; timestamp: string; icon: string; }
interface TeamActivityFeedProps { items: FeedItem[]; total: number; topContributor: string | null; }

export function TeamActivityFeed({ items, total, topContributor }: TeamActivityFeedProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📡 Team Activity</h3>
        <span className="text-xs text-gray-400">{total} events</span>
      </div>
      {topContributor && (
        <div className="px-4 py-2 bg-blue-50 dark:bg-blue-900/20 text-xs text-blue-600 dark:text-blue-400">
          🏅 Top contributor: <strong>{topContributor}</strong>
        </div>
      )}
      <div className="divide-y dark:divide-gray-700 max-h-96 overflow-y-auto">
        {items.map((item, i) => (
          <div key={i} className="flex gap-3 p-3 text-sm">
            <span className="text-lg">{item.icon}</span>
            <div className="flex-1 min-w-0">
              <div className="flex justify-between">
                <span className="font-medium">{item.user}</span>
                <time className="text-xs text-gray-400 whitespace-nowrap">{item.timestamp.slice(0, 10)}</time>
              </div>
              <p className="text-gray-500 truncate">{item.message}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
