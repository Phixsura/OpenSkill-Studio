"use client";
export function FleetAiDataPipePanel({ pipelines, active, records, qualityScore }: { pipelines: number; active: number; records: number; qualityScore: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Data Pipeline</h3>
    <div className="text-sm">{active}/{pipelines} active · {records.toLocaleString()} records · {qualityScore}% quality</div>
  </div>);
}
