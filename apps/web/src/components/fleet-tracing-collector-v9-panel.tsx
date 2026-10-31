"use client";
export function FleetTracingCollectorV9Panel({ collectors, sps }: { collectors: number; sps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Tracing Collector v9</h3>
    <div className="text-sm">{collectors} collectors · {sps.toLocaleString()} spans/s</div>
  </div>);
}
