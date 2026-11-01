"use client";
export function FleetHonoPanel({ apps, deployed, rps, avgLatency }: { apps: number; deployed: number; rps: number; avgLatency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔥 Hono</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {rps.toLocaleString()} rps · {avgLatency}ms</div>
  </div>);
}
