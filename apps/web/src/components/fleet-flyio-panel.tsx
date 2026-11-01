"use client";
export function FleetFlyioPanel({ apps, running, machines, regions }: { apps: number; running: number; machines: number; regions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✈️ Fly.io</h3>
    <div className="text-sm">{running}/{apps} running · {machines} machines · {regions} regions</div>
  </div>);
}
