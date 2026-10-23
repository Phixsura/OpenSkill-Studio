"use client";

interface VersionEntry { version: string; publishedAt: string; author: string;
  changeCount: number; downloads: number; isLatest: boolean; isPrerelease: boolean; }
interface VersionHistoryListProps { versions: VersionEntry[]; latest: string | null; }

export function VersionHistoryList({ versions, latest }: VersionHistoryListProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Version History</h3>
        {latest && <span className="text-xs text-gray-400">Latest: v{latest}</span>}
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {versions.map(v => (
          <div key={v.version} className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold font-mono">v{v.version}</span>
              {v.isLatest && <span className="rounded bg-green-100 px-1.5 py-0.5 text-xs text-green-700 dark:bg-green-900/30">Latest</span>}
              {v.isPrerelease && <span className="rounded bg-yellow-100 px-1.5 py-0.5 text-xs text-yellow-700 dark:bg-yellow-900/30">Pre-release</span>}
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              <span>{v.changeCount} changes</span>
              <span>{v.downloads.toLocaleString()} downloads</span>
              <span>by {v.author}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
