"use client";

interface SchemaDiffViewerProps { added: string[]; removed: string[];
  unchanged: string[]; breaking: boolean; totalChanges: number; }

export function SchemaDiffViewer({ added, removed, unchanged, breaking, totalChanges }: SchemaDiffViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔀 Schema Diff</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{totalChanges} changes</span>
          {breaking && <span className="text-red-500">⚠ Breaking</span>}
        </div>
      </div>
      <div className="p-3 space-y-1 text-xs font-mono">
        {added.map(f => <div key={f} className="text-green-600">+ {f}</div>)}
        {removed.map(f => <div key={f} className="text-red-500">- {f}</div>)}
        {unchanged.slice(0, 5).map(f => <div key={f} className="text-gray-400">  {f}</div>)}
      </div>
    </div>
  );
}
