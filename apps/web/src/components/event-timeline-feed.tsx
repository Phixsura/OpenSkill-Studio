"use client";

interface TimelineItem { id: string; type: string; title: string; description: string;
  timestamp: string; actor: string; icon: string; }
interface EventTimelineFeedProps { items: TimelineItem[]; total: number; }

export function EventTimelineFeed({ items, total }: EventTimelineFeedProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📅 Activity Timeline</h3>
        <span className="text-xs text-gray-400">{total} events</span>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-96 overflow-y-auto">
        {items.map(item => (
          <div key={item.id} className="flex gap-3 px-4 py-3">
            <span className="text-lg">{item.icon}</span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{item.title}</span>
                <time className="text-xs text-gray-400 shrink-0 ml-2">{item.timestamp.slice(0, 10)}</time>
              </div>
              {item.description && <p className="text-xs text-gray-500 truncate">{item.description}</p>}
              <span className="text-xs text-gray-400">{item.actor}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
