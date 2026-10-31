"use client";
export function FleetBigqueryPanel({ datasets, tables, storageTb, queries, bytesProcessed }: { datasets: number; tables: number; storageTb: number; queries: number; bytesProcessed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 BigQuery</h3>
    <div className="text-sm">{datasets} datasets · {tables} tables · {storageTb}TB · {queries.toLocaleString()} queries</div>
  </div>);
}
