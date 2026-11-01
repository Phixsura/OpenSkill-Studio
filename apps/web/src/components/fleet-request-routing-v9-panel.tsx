"use client";
export function FleetRequestRoutingV9Panel({ routers, routes }: { routers: number; routes: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 Request Routing v9</h3>
    <div className="text-sm">{routers} routers · {routes} weighted routes</div>
  </div>);
}
