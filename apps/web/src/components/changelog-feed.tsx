"use client";

interface FeedEntry { appName: string; version: string; date: string; breaking?: boolean; }

interface ChangelogFeedProps { entries: FeedEntry[]; showBreakingOnly?: boolean; }

export function ChangelogFeed({ entries, showBreakingOnly }: ChangelogFeedProps) {
  const filtered = showBreakingOnly ? entries.filter(e => e.breaking) : entries;
  if (filtered.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No changelog entries</p>;
  return (
    <div className="space-y-2">
      {filtered.map((e, i) => (
        <div key={i} className="flex items-center gap-3 rounded border border-gray-200 p-3 dark:border-gray-700">
          <div className="flex-1">
            <span className="font-medium">{e.appName}</span>
            <span className="ml-2 font-mono text-xs text-gray-500">v{e.version}</span>
          </div>
          {e.breaking && <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-800">Breaking</span>}
          <span className="text-xs text-gray-400">{e.date}</span>
        </div>
      ))}
    </div>
  );
}
