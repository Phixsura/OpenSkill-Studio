"use client";

interface TextDiffViewProps { added: string[]; removed: string[]; addedCount: number;
  removedCount: number; similarityPct: number; hasChanges: boolean; }

export function TextDiffView({ added, removed, addedCount, removedCount, similarityPct, hasChanges }: TextDiffViewProps) {
  if (!hasChanges) {
    return <p className="text-sm text-gray-400">No changes detected</p>;
  }
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3 text-xs">
        <span className="text-green-600">+{addedCount} added</span>
        <span className="text-red-600">-{removedCount} removed</span>
        <span className="text-gray-400">{similarityPct}% similar</span>
      </div>
      {removed.length > 0 && (
        <div className="rounded bg-red-50 p-3 dark:bg-red-900/10">
          <p className="text-xs font-medium text-red-600 mb-1">Removed</p>
          <div className="flex flex-wrap gap-1">
            {removed.map((w, i) => <span key={i} className="rounded bg-red-100 px-1.5 py-0.5 text-xs text-red-700 dark:bg-red-900/30 dark:text-red-400 line-through">{w}</span>)}
          </div>
        </div>
      )}
      {added.length > 0 && (
        <div className="rounded bg-green-50 p-3 dark:bg-green-900/10">
          <p className="text-xs font-medium text-green-600 mb-1">Added</p>
          <div className="flex flex-wrap gap-1">
            {added.map((w, i) => <span key={i} className="rounded bg-green-100 px-1.5 py-0.5 text-xs text-green-700 dark:bg-green-900/30 dark:text-green-400">{w}</span>)}
          </div>
        </div>
      )}
    </div>
  );
}
