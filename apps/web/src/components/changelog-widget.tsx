"use client";

interface ChangelogEntry { version: string; title: string; type: string; icon: string; date: string; }
interface ChangelogWidgetProps { appName: string; entries: ChangelogEntry[];
  hasMore: boolean; onViewAll: () => void; }

export function ChangelogWidget({ appName, entries, hasMore, onViewAll }: ChangelogWidgetProps) {
  return (
    <div className="rounded-xl border p-4 dark:border-gray-700">
      <h3 className="text-sm font-semibold mb-3">📝 {appName} Updates</h3>
      <div className="space-y-2">
        {entries.map((e, i) => (
          <div key={i} className="flex items-start gap-2">
            <span className="text-xs mt-0.5">{e.icon}</span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-mono text-gray-400">v{e.version}</span>
                <span className="text-sm truncate">{e.title}</span>
              </div>
              <time className="text-xs text-gray-400">{e.date}</time>
            </div>
          </div>
        ))}
      </div>
      {hasMore && (
        <button onClick={onViewAll} className="mt-3 w-full text-center text-xs text-blue-600 hover:underline">
          View all updates →
        </button>
      )}
    </div>
  );
}
