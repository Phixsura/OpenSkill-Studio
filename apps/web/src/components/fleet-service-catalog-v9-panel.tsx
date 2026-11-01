"use client";
export function FleetServiceCatalogV9Panel({ services, teams }: { services: number; teams: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📚 Service Catalog v9</h3>
    <div className="text-sm">{services} services · {teams} teams</div>
  </div>);
}
