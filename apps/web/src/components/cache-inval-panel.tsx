"use client";

interface CacheEntry { key: string; tags: string[]; ttl: number; }
interface CacheInvalPanelProps { entries: CacheEntry[]; totalEntries: number; uniqueTags: number; }

export function CacheInvalPanel({ entries, totalEntries, uniqueTags }: CacheInvalPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗑️ Cache Invalidation</h3>
        <span className="text-xs text-gray-400">{totalEntries} entries · {uniqueTags} tags</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map(e => (
          <div key={e.key} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{e.key}</span>
            <div className="flex items-center gap-2">
              {e.tags.map(t => (
                <span key={t} className="px-1 rounded bg-gray-100 dark:bg-gray-800 text-[10px]">{t}</span>
              ))}
              <span className="text-gray-400">{e.ttl}s</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
