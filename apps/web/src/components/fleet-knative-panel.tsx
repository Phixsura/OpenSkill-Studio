"use client";
export function FleetKnativePanel({ total, ready, coldStarts, avgLatency }: { total: number; ready: number; coldStarts: number; avgLatency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Knative</h3>
    <div className="text-sm">{ready}/{total} ready · {coldStarts} cold starts/24h · {avgLatency}ms avg</div>
  </div>);
}
