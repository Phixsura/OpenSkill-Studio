"use client";

interface Highlight { type: string; text: string; }
interface Entry { version: string; date: string; highlights: Highlight[]; total_changes: number; }
interface ChangelogWidgetProps { appName: string; entries: Entry[]; hasMore: boolean; onViewAll?: () => void; }

const TYPE_ICONS: Record<string, string> = { feat: "✨", fix: "🐛", perf: "⚡", breaking: "⚠️" };

export function ChangelogWidget({ appName, entries, hasMore, onViewAll }: ChangelogWidgetProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">{appName} Changelog</h3>
      <div className="mt-3 space-y-3">
        {entries.map(e => (
          <div key={e.version} className="border-l-2 border-blue-300 pl-3">
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-sm font-bold">{e.version}</span>
              <span className="text-xs text-gray-400">{e.date.slice(0, 10)}</span>
            </div>
            <ul className="mt-1 space-y-0.5">
              {e.highlights.map((h, i) => (
                <li key={i} className="text-xs text-gray-600 dark:text-gray-400">
                  {TYPE_ICONS[h.type] || "📌"} {h.text}
                </li>
              ))}
              {e.total_changes > e.highlights.length && (
                <li className="text-xs text-gray-400">+{e.total_changes - e.highlights.length} more</li>
              )}
            </ul>
          </div>
        ))}
      </div>
      {hasMore && onViewAll && (
        <button onClick={onViewAll} className="mt-3 text-sm text-blue-600 hover:underline">View all versions →</button>
      )}
    </div>
  );
}
