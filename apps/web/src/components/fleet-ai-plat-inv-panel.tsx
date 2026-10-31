"use client";
export function FleetAiPlatInvPanel({ inventories, active, assets, gpus, storage }: { inventories: number; active: number; assets: number; gpus: number; storage: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 AI Platform Inventory</h3>
    <div className="text-sm">{active}/{inventories} active · {assets.toLocaleString()} assets · {gpus.toLocaleString()} GPUs · {storage}PB</div>
  </div>);
}
