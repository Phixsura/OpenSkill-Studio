"use client";

interface Change { type: string; icon: string; text: string; }
interface VersionChangelog { version: string; date: string; summary: string;
  changes: Change[]; changeCount: number; }
interface AppChangelogViewProps { versions: VersionChangelog[]; totalChanges: number; }

export function AppChangelogView({ versions, totalChanges }: AppChangelogViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Changelog</h3>
        <span className="text-xs text-gray-400">{totalChanges} changes</span>
      </div>
      {versions.map(v => (
        <div key={v.version} className="border-b last:border-0 dark:border-gray-700">
          <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800">
            <span className="text-sm font-bold font-mono">v{v.version}</span>
            <span className="text-xs text-gray-400 ml-2">{v.date}</span>
            {v.summary && <span className="text-xs text-gray-500 ml-2">— {v.summary}</span>}
          </div>
          <div className="px-4 py-2 space-y-1">
            {v.changes.map((c, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span>{c.icon}</span><span>{c.text}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
