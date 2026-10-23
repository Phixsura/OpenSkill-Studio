"use client";

interface Entry { text: string; type: string; }
interface Release { version: string; date: string | null; entries: Entry[]; }
interface ChangelogTimelineProps { releases: Release[]; totalEntries: number; }

const typeIcons: Record<string, string> = { feat: "✨", fix: "🐛", other: "📌" };

export function ChangelogTimeline({ releases, totalEntries }: ChangelogTimelineProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Changelog</h3>
        <span className="text-xs text-gray-400">{releases.length} releases · {totalEntries} changes</span>
      </div>
      {releases.map(r => (
        <div key={r.version} className="relative pl-6 border-l-2 border-gray-200 dark:border-gray-700">
          <div className="absolute -left-2 top-0 h-4 w-4 rounded-full bg-blue-600" />
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-bold">v{r.version}</span>
            {r.date && <span className="text-xs text-gray-400">{r.date}</span>}
          </div>
          <ul className="space-y-1">
            {r.entries.map((e, i) => (
              <li key={i} className="flex items-start gap-1.5 text-sm">
                <span className="text-xs">{typeIcons[e.type] ?? "📌"}</span>
                <span>{e.text}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
