"use client";

interface AppVersion { version: string; changelog: string; latest: boolean; sizeKb: number; }
interface VersionHistoryListProps { versions: AppVersion[]; appId: string;
  onRollback: (version: string) => void; }

export function VersionHistoryList({ versions, appId, onRollback }: VersionHistoryListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 Version History</h3>
        <p className="text-xs text-gray-400">{appId} · {versions.length} versions</p>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {versions.map(v => (
          <div key={v.version} className={`px-4 py-3 ${v.latest ? "bg-blue-50 dark:bg-blue-900/10" : ""}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-mono font-bold">v{v.version}</span>
                {v.latest && <span className="text-xs px-1.5 py-0.5 rounded bg-green-100 text-green-700">Latest</span>}
              </div>
              {!v.latest && (
                <button onClick={() => onRollback(v.version)}
                  className="text-xs px-2 py-1 border border-yellow-200 text-yellow-700 rounded hover:bg-yellow-50">Rollback</button>
              )}
            </div>
            {v.changelog && <p className="text-xs text-gray-500 mt-1">{v.changelog}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
