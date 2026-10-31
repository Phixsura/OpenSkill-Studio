"use client";
export function FleetContainerProbeV9Panel({ containers, liveness }: { containers: number; liveness: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐳 Container Probe v9</h3>
    <div className="text-sm">{containers} containers · {liveness} liveness</div>
  </div>);
}
