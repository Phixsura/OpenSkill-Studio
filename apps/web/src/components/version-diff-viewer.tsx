"use client";

interface DiffEntry { key: string; value?: unknown; old?: unknown; new?: unknown; }
interface VersionDiffViewerProps { added: DiffEntry[]; removed: DiffEntry[];
  changed: DiffEntry[]; totalChanges: number; hasBreaking: boolean; }

export function VersionDiffViewer({ added, removed, changed, totalChanges, hasBreaking }: VersionDiffViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔀 Version Diff</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{totalChanges} changes</span>
          {hasBreaking && <span className="text-red-500 font-medium">⚠ Breaking</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700 text-sm">
        {added.map(e => (
          <div key={e.key} className="flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-green-900/10">
            <span className="text-green-600 font-mono text-xs">+ added</span>
            <span className="font-mono">{e.key}</span>
            <span className="text-gray-400 ml-auto">{String(e.value)}</span>
          </div>
        ))}
        {removed.map(e => (
          <div key={e.key} className="flex items-center gap-2 px-4 py-2 bg-red-50 dark:bg-red-900/10">
            <span className="text-red-600 font-mono text-xs">- removed</span>
            <span className="font-mono">{e.key}</span>
            <span className="text-gray-400 ml-auto">{String(e.value)}</span>
          </div>
        ))}
        {changed.map(e => (
          <div key={e.key} className="flex items-center gap-2 px-4 py-2 bg-yellow-50 dark:bg-yellow-900/10">
            <span className="text-yellow-600 font-mono text-xs">~ changed</span>
            <span className="font-mono">{e.key}</span>
            <span className="text-gray-400 ml-auto">{String(e.old)} → {String(e.new)}</span>
          </div>
        ))}
        {totalChanges === 0 && <div className="px-4 py-3 text-gray-400 text-center">No differences</div>}
      </div>
    </div>
  );
}
