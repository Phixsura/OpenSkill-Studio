"use client";

interface TopoDiffViewerProps { nodesAdded: string[]; nodesRemoved: string[];
  edgesAdded: string[]; edgesRemoved: string[]; totalChanges: number; breaking: boolean; }

export function TopoDiffViewer({ nodesAdded, nodesRemoved, edgesAdded, edgesRemoved, totalChanges, breaking }: TopoDiffViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔀 Topology Diff</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{totalChanges} changes</span>
          {breaking && <span className="text-red-500">⚠ Breaking</span>}
        </div>
      </div>
      <div className="p-3 space-y-0.5 text-xs font-mono">
        {nodesAdded.map(n => <div key={n} className="text-green-600">+ node: {n}</div>)}
        {nodesRemoved.map(n => <div key={n} className="text-red-500">- node: {n}</div>)}
        {edgesAdded.map(e => <div key={e} className="text-green-600">+ edge: {e}</div>)}
        {edgesRemoved.map(e => <div key={e} className="text-red-500">- edge: {e}</div>)}
        {totalChanges === 0 && <div className="text-gray-400">No changes</div>}
      </div>
    </div>
  );
}
