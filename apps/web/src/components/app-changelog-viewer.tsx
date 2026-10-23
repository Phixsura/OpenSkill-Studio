"use client";

interface Entry { type: string; text: string; }
interface Release { version: string; date: string; entryCount: number; entries: Entry[]; hasBreaking: boolean; }
interface AppChangelogViewerProps { appName: string; releases: Release[]; totalChanges: number; }

const typeIcons: Record<string, string> = {
  added: "✨", fixed: "🐛", changed: "🔄", breaking: "💥", removed: "🗑️", security: "🔒",
};

export function AppChangelogViewer({ appName, releases, totalChanges }: AppChangelogViewerProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">{appName} Changelog</h2>
        <span className="text-xs text-gray-400">{releases.length} releases · {totalChanges} changes</span>
      </div>
      {releases.map(r => (
        <div key={r.version} className="rounded-xl border p-4 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-bold">v{r.version}</span>
            {r.hasBreaking && <span className="rounded bg-red-100 px-1.5 py-0.5 text-xs text-red-700 dark:bg-red-900/30">Breaking</span>}
            <span className="ml-auto text-xs text-gray-400">{r.date}</span>
          </div>
          <ul className="space-y-1">
            {r.entries.map((e, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span className="text-xs">{typeIcons[e.type] ?? "📌"}</span>
                <span className={e.type === "breaking" ? "font-medium text-red-600" : ""}>{e.text}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
