"use client";
interface VersionChange { service: string; from: string; to: string; }
interface DeployDiffRptPanelProps { added: string[]; removed: string[]; upgraded: VersionChange[];
  downgraded: VersionChange[]; totalChanges: number; }
export function DeployDiffRptPanel({ added, removed, upgraded, downgraded, totalChanges }: DeployDiffRptPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Deploy Diff</h3>
        <span className="text-xs text-gray-400">{totalChanges} changes</span>
      </div>
      <div className="p-4 text-xs font-mono space-y-0.5">
        {added.map(a => <div key={a} className="text-green-600">+ {a}</div>)}
        {removed.map(r => <div key={r} className="text-red-600">- {r}</div>)}
        {upgraded.map(u => <div key={u.service} className="text-blue-500">↑ {u.service}: {u.from} → {u.to}</div>)}
        {downgraded.map(d => <div key={d.service} className="text-yellow-600">↓ {d.service}: {d.from} → {d.to}</div>)}
      </div>
    </div>
  );
}
