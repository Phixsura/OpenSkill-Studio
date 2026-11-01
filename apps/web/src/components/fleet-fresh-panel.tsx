"use client";
export function FleetFreshPanel({ apps, running, islands, routes }: { apps: number; running: number; islands: number; routes: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🍋 Fresh</h3>
    <div className="text-sm">{running}/{apps} running · {islands} islands · {routes} routes</div>
  </div>);
}
