"use client";

interface ChangelogEntry { type: string; icon: string; message: string; breaking: boolean; }
interface Release { version: string; date: string; entries: ChangelogEntry[]; has_breaking: boolean; }
interface ChangelogViewProps { releases: Release[]; }

export function ChangelogView({ releases }: ChangelogViewProps) {
  return (
    <div className="space-y-6">
      {releases.map(rel => (
        <div key={rel.version} className="rounded-lg border p-4 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-bold">v{rel.version}</h3>
            {rel.has_breaking && <span className="rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">Breaking</span>}
            <time className="ml-auto text-xs text-gray-400">{rel.date}</time>
          </div>
          <ul className="mt-3 space-y-1.5">
            {rel.entries.map((e, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span>{e.icon}</span>
                <span className={e.breaking ? "font-medium text-red-600 dark:text-red-400" : ""}>{e.message}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
