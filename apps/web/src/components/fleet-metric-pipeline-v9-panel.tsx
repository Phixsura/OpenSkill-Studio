"use client";
export function FleetMetricPipelineV9Panel({ collectors, mps }: { collectors: number; mps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Metric Pipeline v9</h3>
    <div className="text-sm">{collectors} collectors · {mps.toLocaleString()} m/s</div>
  </div>);
}
