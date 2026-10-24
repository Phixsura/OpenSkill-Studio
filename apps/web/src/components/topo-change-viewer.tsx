"use client";

interface TopoChangeViewerProps { servicesAdded: string[]; servicesRemoved: string[];
  connectionsAdded: string[]; connectionsRemoved: string[];
  totalChanges: number; breaking: boolean; }

export function TopoChangeViewer({ servicesAdded, servicesRemoved, connectionsAdded, connectionsRemoved, totalChanges, breaking }: TopoChangeViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Topology Changes</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{totalChanges} changes</span>
          {breaking && <span className="text-red-500">⚠ Breaking</span>}
        </div>
      </div>
      <div className="p-3 text-xs font-mono space-y-0.5">
        {servicesAdded.map(s => <div key={s} className="text-green-600">+ service: {s}</div>)}
        {servicesRemoved.map(s => <div key={s} className="text-red-500">- service: {s}</div>)}
        {connectionsAdded.map(c => <div key={c} className="text-green-600">+ link: {c}</div>)}
        {connectionsRemoved.map(c => <div key={c} className="text-red-500">- link: {c}</div>)}
        {totalChanges === 0 && <div className="text-gray-400">No changes</div>}
      </div>
    </div>
  );
}
