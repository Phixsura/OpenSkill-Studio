"use client";

interface BookmarkItem { extensionId: string; collection: string; note: string; tags: string[]; }

export function BookmarkListPanel({
  bookmarks, collections, onRemove, onFilter,
}: {
  bookmarks: BookmarkItem[]; collections: string[];
  onRemove?: (extId: string) => void; onFilter?: (collection: string | null) => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔖 Bookmarks</h2>
        <span className="text-sm text-gray-500">{bookmarks.length} saved</span>
      </div>
      <div className="flex gap-1">
        <button onClick={() => onFilter?.(null)} className="text-xs px-2.5 py-1 rounded-full bg-blue-600 text-white">All</button>
        {collections.map((c) => (
          <button key={c} onClick={() => onFilter?.(c)}
            className="text-xs px-2.5 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500">{c}</button>
        ))}
      </div>
      <div className="space-y-1">
        {bookmarks.map((b) => (
          <div key={b.extensionId} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
            <div>
              <code className="text-sm font-semibold">{b.extensionId}</code>
              {b.note && <p className="text-xs text-gray-500">{b.note}</p>}
              <div className="flex gap-1 mt-0.5">
                {b.tags.map((t) => <span key={t} className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{t}</span>)}
              </div>
            </div>
            <button onClick={() => onRemove?.(b.extensionId)} className="text-xs text-red-500">✕</button>
          </div>
        ))}
      </div>
    </div>
  );
}
