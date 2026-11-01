"use client";
export function FleetEventRouterV9Panel({ routes, eps }: { routes: number; eps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 Event Router v9</h3>
    <div className="text-sm">{routes} routes · {eps.toLocaleString()} events/s</div>
  </div>);
}
