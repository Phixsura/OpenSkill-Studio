"use client";
export function FleetAiCkptMgrPanel({ managers, active, checkpoints, storageTb, autoCleanup }: { managers: number; active: number; checkpoints: number; storageTb: number; autoCleanup: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 AI Checkpoint Mgr</h3>
    <div className="text-sm">{active}/{managers} active · {checkpoints.toLocaleString()} ckpts · {storageTb}TB · {autoCleanup ? "✅" : "⚠️"} cleanup</div>
  </div>);
}
