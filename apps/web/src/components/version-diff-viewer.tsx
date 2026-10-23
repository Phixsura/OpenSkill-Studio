"use client";

interface ModifiedField { field: string; old: unknown; new: unknown; }
interface VersionDiffViewerProps { addedFields: string[]; removedFields: string[];
  modifiedFields: ModifiedField[]; totalChanges: number; hasBreaking: boolean; }

export function VersionDiffViewer({ addedFields, removedFields, modifiedFields, totalChanges, hasBreaking }: VersionDiffViewerProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Version Diff</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">{totalChanges} changes</span>
          {hasBreaking && <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-700 dark:bg-red-900/30">Breaking</span>}
        </div>
      </div>
      {addedFields.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-green-600">+ Added</h3>
          {addedFields.map(f => <p key={f} className="ml-2 font-mono text-xs text-green-500">+ {f}</p>)}
        </div>
      )}
      {removedFields.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-red-600">− Removed</h3>
          {removedFields.map(f => <p key={f} className="ml-2 font-mono text-xs text-red-500">- {f}</p>)}
        </div>
      )}
      {modifiedFields.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-yellow-600">~ Modified</h3>
          {modifiedFields.map(m => (
            <div key={m.field} className="ml-2 font-mono text-xs">
              <span className="text-gray-400">{m.field}: </span>
              <span className="text-red-400">{String(m.old)}</span>
              <span className="text-gray-400"> → </span>
              <span className="text-green-400">{String(m.new)}</span>
            </div>
          ))}
        </div>
      )}
      {totalChanges === 0 && <p className="text-sm text-gray-400">No changes between versions</p>}
    </div>
  );
}
