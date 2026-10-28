"use client";

interface RSSFeedInfo {
  title: string;
  link: string;
  language: string;
  item_count: number;
  latest_items: { title: string; version: string; date: string }[];
}

interface ChangelogRSSCardProps {
  feed: RSSFeedInfo;
  appName: string;
}

export default function ChangelogRSSCard({ feed, appName }: ChangelogRSSCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">RSS Feed</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded bg-orange-100 px-1.5 py-0.5 text-[10px] font-medium text-orange-700 dark:bg-orange-900/30 dark:text-orange-400">
            RSS 2.0
          </span>
          <span className="text-xs text-gray-400">{feed.item_count} items</span>
        </div>
      </div>

      <div className="mb-3 rounded bg-gray-50 px-3 py-2 dark:bg-gray-800/50">
        <p className="text-xs font-medium text-gray-700 dark:text-gray-300">{feed.title}</p>
        <p className="mt-0.5 truncate font-mono text-[11px] text-gray-400">{feed.link}</p>
      </div>

      {feed.latest_items.length > 0 ? (
        <div>
          <p className="mb-1.5 text-xs font-medium text-gray-500">Latest</p>
          <div className="space-y-1">
            {feed.latest_items.map((item) => (
              <div key={item.version} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-gray-500">v{item.version}</span>
                  <span className="text-gray-700 dark:text-gray-300">{item.title}</span>
                </div>
                <span className="text-[11px] text-gray-400">{item.date}</span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-center text-sm text-gray-400">No items published</p>
      )}
    </div>
  );
}
