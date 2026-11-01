"use client";
export function FleetLogRouterV9Panel({ routes, destinations }: { routes: number; destinations: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Log Router v9</h3>
    <div className="text-sm">{routes} routes · {destinations} destinations</div>
  </div>);
}
