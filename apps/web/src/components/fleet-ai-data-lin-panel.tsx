"use client";
export function FleetAiDataLinPanel({ trackers, active, datasets, transforms, depth }: { trackers: number; active: number; datasets: number; transforms: number; depth: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 AI Data Lineage</h3>
    <div className="text-sm">{active}/{trackers} active · {datasets} datasets · {transforms.toLocaleString()} transforms · depth {depth}</div>
  </div>);
}
