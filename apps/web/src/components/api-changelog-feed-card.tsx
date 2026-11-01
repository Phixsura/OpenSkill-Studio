"use client";

interface FeedEntryInfo {
  entry_id: string;
  version: string;
  title: string;
  summary: string;
}

interface APIChangelogFeedCardProps {
  entries: FeedEntryInfo[];
  totalCount: number;
  currentPage: number;
  totalPages: number;
  appName: string;
}

export default function APIChangelogFeedCard({
  entries,
  totalCount,
  currentPage,
  totalPages,
  appName,
}: APIChangelogFeedCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📰 Changelog Feed
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {totalCount} entries · page {currentPage}/{totalPages}
        </span>
      </div>

      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No changelog entries</p>
      ) : (
        <div className="space-y-2">
          {entries.map((e) => (
            <div
              key={e.entry_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                  {e.title}
                </span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">
                  {e.version}
                </span>
              </div>
              {e.summary && <p className="mt-0.5 text-[10px] text-gray-400">{e.summary}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
