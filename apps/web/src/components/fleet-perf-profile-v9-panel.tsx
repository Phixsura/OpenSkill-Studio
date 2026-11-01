"use client";
export function FleetPerfProfileV9Panel({ profiles, hotspots }: { profiles: number; hotspots: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔬 Perf Profile v9</h3>
    <div className="text-sm">{profiles} profiles · {hotspots} hotspots</div>
  </div>);
}
