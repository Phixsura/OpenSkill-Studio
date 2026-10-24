"use client";
export function FleetDatasetsPanel({ repos, active, datasets, totalRows }: { repos: number; active: number; datasets: number; totalRows: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Datasets</h3>
    <div className="text-sm">{active}/{repos} active · {datasets} datasets · {totalRows.toLocaleString()} rows</div>
  </div>);
}
