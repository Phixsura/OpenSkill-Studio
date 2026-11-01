"use client";
export function FleetAiDataProfPanel({ profilers, active, datasets, columns, anomalies }: { profilers: number; active: number; datasets: number; columns: number; anomalies: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Data Profiler</h3>
    <div className="text-sm">{active}/{profilers} active · {datasets} datasets · {columns.toLocaleString()} columns · {anomalies} anomalies</div>
  </div>);
}
