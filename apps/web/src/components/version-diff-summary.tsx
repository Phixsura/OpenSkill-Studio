"use client";

interface Modified { field: string; old_type: string; new_type: string; type_changed: boolean; }
interface VersionDiffSummaryProps { added: string[]; removed: string[]; modified: Modified[];
  totalChanges: number; breaking: boolean; compatible: boolean; }

export function VersionDiffSummary({ added, removed, modified, totalChanges, breaking, compatible }: VersionDiffSummaryProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">API Diff</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${compatible ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {compatible ? "✅ Compatible" : "⚠️ Breaking Changes"}
        </span>
      </div>
      <p className="text-xs text-gray-400">{totalChanges} changes detected</p>
      {added.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-green-600">+ Added ({added.length})</h3>
          {added.map(f => <p key={f} className="ml-4 font-mono text-xs text-green-500">+ {f}</p>)}
        </div>
      )}
      {removed.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-red-600">− Removed ({removed.length})</h3>
          {removed.map(f => <p key={f} className="ml-4 font-mono text-xs text-red-500">- {f}</p>)}
        </div>
      )}
      {modified.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-yellow-600">~ Modified ({modified.length})</h3>
          {modified.map(m => (
            <p key={m.field} className="ml-4 font-mono text-xs">
              <span className="text-gray-400">{m.field}</span>
              {m.type_changed && <span className="text-red-500"> ({m.old_type} → {m.new_type})</span>}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
