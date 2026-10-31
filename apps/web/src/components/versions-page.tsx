"use client";

interface Version { version: string; publishedAt: string; author: string; downloads: number;
  changeCount: number; isCurrent: boolean; isPrerelease: boolean; canRollback: boolean; }
interface VersionsPageProps { appName: string; versions: Version[]; current: string;
  totalDownloads: number; onRollback: (version: string) => void; onPublish: () => void; }

export function VersionsPage({ appName, versions, current, totalDownloads, onRollback, onPublish }: VersionsPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📦 {appName} Versions</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{versions.length} versions · {totalDownloads.toLocaleString()} downloads</span>
          <button onClick={onPublish} className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white">+ New Version</button>
        </div>
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {versions.map(v => (
          <div key={v.version} className="flex items-center justify-between px-4 py-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold font-mono">v{v.version}</span>
                {v.isCurrent && <span className="rounded bg-green-100 px-1.5 py-0.5 text-xs text-green-700 dark:bg-green-900/30">Current</span>}
                {v.isPrerelease && <span className="rounded bg-yellow-100 px-1.5 py-0.5 text-xs text-yellow-700 dark:bg-yellow-900/30">Pre-release</span>}
              </div>
              <p className="text-xs text-gray-400 mt-0.5">by {v.author} · {v.changeCount} changes · {v.downloads.toLocaleString()} downloads</p>
            </div>
            <div className="flex items-center gap-2">
              <time className="text-xs text-gray-400">{v.publishedAt}</time>
              {v.canRollback && (
                <button onClick={() => onRollback(v.version)} className="text-xs text-blue-600 hover:underline">Rollback</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
