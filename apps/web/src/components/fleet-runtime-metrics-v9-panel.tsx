"use client";
export function FleetRuntimeMetricsV9Panel({ apps, memory }: { apps: number; memory: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Runtime Metrics v9</h3>
    <div className="text-sm">{apps} apps · {memory} GB memory</div>
  </div>);
}
