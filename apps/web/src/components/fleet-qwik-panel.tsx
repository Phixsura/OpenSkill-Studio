"use client";
export function FleetQwikPanel({ apps, deployed, routes, avgTtfb }: { apps: number; deployed: number; routes: number; avgTtfb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Qwik</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {routes} routes · {avgTtfb}ms TTFB</div>
  </div>);
}
