"use client";

interface DiffEndpoint { method?: string; path?: string; endpoint?: string; }
interface VersionDiffViewerProps { added: DiffEndpoint[]; removed: DiffEndpoint[];
  changed: DiffEndpoint[]; summary: string; breaking: boolean; }

export function VersionDiffViewer({ added, removed, changed, summary, breaking }: VersionDiffViewerProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔄 API Version Diff</h3>
        <div className="flex gap-2">
          <span className="text-xs font-mono text-gray-400">{summary}</span>
          {breaking && <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">Breaking</span>}
        </div>
      </div>
      {added.length > 0 && (
        <div className="mb-3">
          <h4 className="text-xs font-semibold text-green-600 mb-1">+ Added ({added.length})</h4>
          {added.map((e, i) => <p key={i} className="text-sm text-green-600 font-mono">+ {e.method} {e.path}</p>)}
        </div>
      )}
      {removed.length > 0 && (
        <div className="mb-3">
          <h4 className="text-xs font-semibold text-red-600 mb-1">- Removed ({removed.length})</h4>
          {removed.map((e, i) => <p key={i} className="text-sm text-red-600 font-mono">- {e.method} {e.path}</p>)}
        </div>
      )}
      {changed.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-yellow-600 mb-1">~ Changed ({changed.length})</h4>
          {changed.map((e, i) => <p key={i} className="text-sm text-yellow-600 font-mono">~ {e.endpoint}</p>)}
        </div>
      )}
    </div>
  );
}
