"use client";
export function FleetCpuProfilerV9Panel({ profiles, hotspots }: { profiles: number; hotspots: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔬 CPU Profiler v9</h3>
    <div className="text-sm">{profiles} profiles · {hotspots} hotspots</div>
  </div>);
}
