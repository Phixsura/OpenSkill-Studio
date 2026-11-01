"use client";

interface TimelineItem {
  id: string; title: string; description: string; icon: string;
  timestamp: string; actor: string; type: string;
}
interface TimelineFeedProps { items: TimelineItem[]; }

export function TimelineFeed({ items }: TimelineFeedProps) {
  return (
    <div className="relative space-y-6 pl-8">
      <div className="absolute left-3 top-2 bottom-2 w-px bg-gray-200 dark:bg-gray-700" />
      {items.map(item => (
        <div key={item.id} className="relative">
          <span className="absolute -left-5 flex h-6 w-6 items-center justify-center rounded-full bg-white text-sm dark:bg-gray-900 ring-2 ring-gray-200 dark:ring-gray-700">
            {item.icon}
          </span>
          <div className="rounded-lg border p-3 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{item.title}</span>
              <time className="text-xs text-gray-400">{new Date(item.timestamp).toLocaleDateString()}</time>
            </div>
            {item.description && <p className="mt-1 text-xs text-gray-500">{item.description}</p>}
            <p className="mt-1 text-xs text-gray-400">by {item.actor}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
