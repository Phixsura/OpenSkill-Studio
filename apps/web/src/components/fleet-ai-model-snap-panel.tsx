"use client";
export function FleetAiModelSnapPanel({ managers, active, snapshots, storageTb, restorations }: { managers: number; active: number; snapshots: number; storageTb: number; restorations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📸 AI Model Snapshot</h3>
    <div className="text-sm">{active}/{managers} active · {snapshots.toLocaleString()} snapshots · {storageTb}TB · {restorations} restorations</div>
  </div>);
}
