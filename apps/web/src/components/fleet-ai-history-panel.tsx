"use client";
export function FleetAiHistoryPanel({ stores, active, interactions, storageGb }: { stores: number; active: number; interactions: number; storageGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 AI History</h3>
    <div className="text-sm">{active}/{stores} active · {interactions.toLocaleString()} interactions · {storageGb}GB</div>
  </div>);
}
