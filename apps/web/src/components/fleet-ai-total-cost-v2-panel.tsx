"use client";
export function FleetAiTotalCostV2Panel({ trackers, active, compute, storage, network, total }: { trackers: number; active: number; compute: number; storage: number; network: number; total: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Total Cost v2</h3>
    <div className="text-sm">{active}/{trackers} active · compute ${compute.toLocaleString()} · storage ${storage.toLocaleString()} · network ${network.toLocaleString()} · total ${total.toLocaleString()}</div>
  </div>);
}
