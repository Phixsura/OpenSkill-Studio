"use client";
export function FleetAiDataPipePanel({ pipelines, active, records, throughput }: { pipelines: number; active: number; records: number; throughput: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI Data Pipeline</h3>
    <div className="text-sm">{active}/{pipelines} active · {records.toLocaleString()} records · {throughput} MB/s</div>
  </div>);
}
