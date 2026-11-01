"use client";
export function FleetAiDataopsV8Panel({ systems, active, pipelines, datasets, quality }: { systems: number; active: number; pipelines: number; datasets: number; quality: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 AI DataOps v8</h3>
    <div className="text-sm">{active}/{systems} active · {pipelines} pipelines · {datasets.toLocaleString()} datasets · {quality}% quality</div>
  </div>);
}
