"use client";
export function FleetEtlMonitorV9Panel({ jobs, rows }: { jobs: number; rows: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 ETL Monitor v9</h3>
    <div className="text-sm">{jobs} jobs · {rows.toLocaleString()} rows</div>
  </div>);
}
