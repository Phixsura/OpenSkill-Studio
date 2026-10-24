"use client";
export function FleetObservabilityPipelineV9Panel({ stages, throughput }: { stages: number; throughput: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👁️ Obs Pipeline v9</h3>
    <div className="text-sm">{stages} stages · {throughput.toLocaleString()} eps</div>
  </div>);
}
