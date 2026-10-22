"use client";

interface ChangelogEntry { version: string; released_at: string; categories: Record<string, string[]>; total_changes: number; }
interface ChangelogTimelineProps { entries: ChangelogEntry[]; }

const CAT_ICONS: Record<string, string> = { added: "🟢", changed: "🔵", fixed: "🟡", removed: "🔴" };

export function ChangelogTimeline({ entries }: ChangelogTimelineProps) {
  if (entries.length === 0) return <p className="text-sm text-gray-400">No changelog entries yet.</p>;
  return (
    <div className="space-y-6">
      {entries.map(e => (
        <div key={e.version} className="border-l-2 border-blue-300 pl-4">
          <div className="flex items-baseline gap-2">
            <h3 className="text-lg font-bold">{e.version}</h3>
            <span className="text-xs text-gray-400">{e.released_at.slice(0, 10)}</span>
            <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-700">{e.total_changes} changes</span>
          </div>
          {Object.entries(e.categories).map(([cat, items]) => (
            <div key={cat} className="mt-2">
              <h4 className="text-sm font-medium">{CAT_ICONS[cat] || "📌"} {cat.charAt(0).toUpperCase() + cat.slice(1)}</h4>
              <ul className="ml-4 mt-1 list-disc text-sm text-gray-600 dark:text-gray-400">
                {items.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
