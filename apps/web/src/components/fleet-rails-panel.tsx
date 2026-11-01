"use client";
export function FleetRailsPanel({ apps, running, rps, dbPoolPct }: { apps: number; running: number; rps: number; dbPoolPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💎 Rails</h3>
    <div className="text-sm">{running}/{apps} running · {rps.toLocaleString()} rps · {dbPoolPct}% pool</div>
  </div>);
}
