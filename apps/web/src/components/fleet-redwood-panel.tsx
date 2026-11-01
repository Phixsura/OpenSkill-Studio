"use client";
export function FleetRedwoodPanel({ apps, deployed, cells, services }: { apps: number; deployed: number; cells: number; services: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌲 RedwoodJS</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {cells} cells · {services} services</div>
  </div>);
}
