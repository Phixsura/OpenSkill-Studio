"use client";
export function FleetDataPipelineV9Panel({ jobs, rows }: { jobs: number; rows: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 Data Pipeline v9</h3>
    <div className="text-sm">{jobs} jobs · {rows.toLocaleString()} rows</div>
  </div>);
}
