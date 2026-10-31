"use client";

interface RssItem { title: string; version: string; date: string; description: string; changeCount: number; }
interface ChangelogRssPreviewProps { title: string; items: RssItem[]; lastUpdated: string; }

export function ChangelogRssPreview({ title, items, lastUpdated }: ChangelogRssPreviewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📡 {title}</h3>
        <span className="text-xs text-gray-400">Updated: {lastUpdated}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {items.map(item => (
          <div key={item.version} className="px-4 py-3">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-bold">{item.title}</span>
              <span className="text-xs text-gray-400">{item.date}</span>
              <span className="text-xs px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded">{item.changeCount} changes</span>
            </div>
            <p className="text-xs text-gray-500">{item.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
