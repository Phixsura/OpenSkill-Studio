"use client";
export function FleetSveltekitPanel({ apps, deployed, routes, ssrPct }: { apps: number; deployed: number; routes: number; ssrPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🟠 SvelteKit</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {routes} routes · {ssrPct}% SSR</div>
  </div>);
}
