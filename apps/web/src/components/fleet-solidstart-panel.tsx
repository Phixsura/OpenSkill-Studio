"use client";
export function FleetSolidstartPanel({ apps, running, routes, signals }: { apps: number; running: number; routes: number; signals: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔵 SolidStart</h3>
    <div className="text-sm">{running}/{apps} running · {routes} routes · {signals} signals</div>
  </div>);
}
