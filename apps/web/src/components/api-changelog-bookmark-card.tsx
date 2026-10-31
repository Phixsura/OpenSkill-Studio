"use client";

interface BookmarkInfo { entry_id: string; title: string; note: string; }
interface Props { bookmarks: BookmarkInfo[]; appName: string; }

export default function APIChangelogBookmarkCard({ bookmarks, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔖 Bookmarks</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{bookmarks.length} saved</span>
      </div>
      {bookmarks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No bookmarks</p>
      ) : (
        <div className="space-y-1">
          {bookmarks.map((b) => (
            <div key={b.entry_id} className="text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{b.title}</span>
              {b.note && <p className="text-[9px] text-gray-400">{b.note}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
