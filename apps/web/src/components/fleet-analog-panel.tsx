"use client";
export function FleetAnalogPanel({ apps, deployed, pages, apiRoutes }: { apps: number; deployed: number; pages: number; apiRoutes: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🅰️ Analog</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {pages} pages · {apiRoutes} API routes</div>
  </div>);
}
