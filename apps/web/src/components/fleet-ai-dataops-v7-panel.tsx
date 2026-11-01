"use client";
export function FleetAiDataopsV7Panel({ systems, active, pipelines, datasets, quality, freshness }: { systems: number; active: number; pipelines: number; datasets: number; quality: number; freshness: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 AI DataOps v7</h3>
    <div className="text-sm">{active}/{systems} active · {pipelines} pipelines · {datasets.toLocaleString()} datasets · {quality}% quality · {freshness}m fresh</div>
  </div>);
}
