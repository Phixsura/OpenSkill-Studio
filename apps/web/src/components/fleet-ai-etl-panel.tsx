"use client";
export function FleetAiEtlPanel({ engines, active, jobs, records, failures }: { engines: number; active: number; jobs: number; records: number; failures: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI ETL Engine</h3>
    <div className="text-sm">{active}/{engines} active · {jobs} jobs · {records.toLocaleString()} records · {failures} failures</div>
  </div>);
}
