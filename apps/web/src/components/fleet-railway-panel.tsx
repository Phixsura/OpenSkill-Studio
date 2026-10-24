"use client";
export function FleetRailwayPanel({ services, deployed, deploys }: { services: number; deployed: number; deploys: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚂 Railway</h3>
    <div className="text-sm">{deployed}/{services} deployed · {deploys} deploys/24h</div>
  </div>);
}
