"use client";
export function FleetAiDataPipeV2Panel({ pipelines, active, stages, records, throughput }: { pipelines: number; active: number; stages: number; records: number; throughput: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI Data Pipeline v2</h3>
    <div className="text-sm">{active}/{pipelines} active · {stages} stages · {records.toLocaleString()} records · {throughput}MB/s</div>
  </div>);
}
