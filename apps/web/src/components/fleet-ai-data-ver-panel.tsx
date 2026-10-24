"use client";
export function FleetAiDataVerPanel({ systems, active, datasets, versions, storageTb }: { systems: number; active: number; datasets: number; versions: number; storageTb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 AI Data Versioning</h3>
    <div className="text-sm">{active}/{systems} active · {datasets} datasets · {versions} versions · {storageTb}TB</div>
  </div>);
}
