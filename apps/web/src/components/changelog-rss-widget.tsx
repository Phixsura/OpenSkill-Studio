"use client";

interface RssEntry { title: string; description: string; date: string; }
interface ChangelogRssWidgetProps { title: string; entries: RssEntry[];
  feedUrl: string; itemCount: number; }

export function ChangelogRssWidget({ title, entries, feedUrl, itemCount }: ChangelogRssWidgetProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📰 {title}</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{itemCount} entries</span>
          <a href={feedUrl} className="text-orange-500 hover:underline">RSS</a>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map((e, i) => (
          <div key={i} className="px-4 py-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{e.title}</span>
              <span className="text-[10px] text-gray-400">{e.date}</span>
            </div>
            <div className="text-xs text-gray-500 mt-0.5">{e.description}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
