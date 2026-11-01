"use client";

interface RSSItemInfo {
  item_id: string;
  title: string;
  version: string;
}

interface ChangelogRSSCardProps {
  feedTitle: string;
  feedLink: string;
  items: RSSItemInfo[];
  appName: string;
}

export default function ChangelogRSSCard({
  feedTitle,
  feedLink,
  items,
  appName,
}: ChangelogRSSCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📡 Changelog RSS
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{items.length} items</span>
      </div>

      <div className="mb-3 rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
        <p className="text-xs font-medium text-gray-700 dark:text-gray-300">{feedTitle}</p>
        <p className="truncate text-[10px] text-gray-400">{feedLink}</p>
      </div>

      {items.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No feed items</p>
      ) : (
        <div className="space-y-1">
          {items.map((i) => (
            <div key={i.item_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{i.title}</span>
              <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">
                {i.version}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
