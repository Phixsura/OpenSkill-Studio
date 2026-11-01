"use client";
export function FleetObservabilityHubV9Panel({ sources, mps }: { sources: number; mps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👁️ Observability Hub v9</h3>
    <div className="text-sm">{sources} sources · {mps.toLocaleString()} metrics/s</div>
  </div>);
}
