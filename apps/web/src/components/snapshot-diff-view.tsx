"use client";

interface SnapshotDiffViewProps {
  added: Record<string, unknown>; removed: Record<string, unknown>;
  changed: Record<string, { before: unknown; after: unknown }>;
  totalChanges: number; hasDrift: boolean;
}

export function SnapshotDiffView({ added, removed, changed, totalChanges, hasDrift }: SnapshotDiffViewProps) {
  if (!hasDrift) return <p className="text-sm text-green-600">✓ No drift detected</p>;
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <span className="text-yellow-600">⚠</span>
        <span className="text-sm font-semibold">{totalChanges} change{totalChanges !== 1 ? "s" : ""} detected</span>
      </div>
      {Object.entries(changed).map(([k, v]) => (
        <div key={k} className="rounded border px-3 py-2 dark:border-gray-700">
          <p className="text-xs font-mono font-medium">{k}</p>
          <div className="flex gap-4 mt-1 text-xs">
            <span className="text-red-500 line-through">{JSON.stringify(v.before)}</span>
            <span>→</span>
            <span className="text-green-600">{JSON.stringify(v.after)}</span>
          </div>
        </div>
      ))}
      {Object.keys(added).length > 0 && (
        <div className="space-y-1">
          {Object.entries(added).map(([k, v]) => (
            <p key={k} className="text-xs text-green-600">+ <span className="font-mono">{k}</span>: {JSON.stringify(v)}</p>
          ))}
        </div>
      )}
      {Object.keys(removed).length > 0 && (
        <div className="space-y-1">
          {Object.entries(removed).map(([k, v]) => (
            <p key={k} className="text-xs text-red-500 line-through">- <span className="font-mono">{k}</span>: {JSON.stringify(v)}</p>
          ))}
        </div>
      )}
    </div>
  );
}
