"use client";
export function FleetPlaygroundV9Panel({ active, cpuHours }: { active: number; cpuHours: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎮 Playground v9</h3>
    <div className="text-sm">{active} active · {cpuHours}h CPU today</div>
  </div>);
}
