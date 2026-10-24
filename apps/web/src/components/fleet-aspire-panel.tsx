"use client";
export function FleetAspirePanel({ apps, running, services, resources }: { apps: number; running: number; services: number; resources: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🟣 .NET Aspire</h3>
    <div className="text-sm">{running}/{apps} running · {services} services · {resources} resources</div>
  </div>);
}
