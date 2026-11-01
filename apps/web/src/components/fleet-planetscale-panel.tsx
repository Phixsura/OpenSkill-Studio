"use client";
export function FleetPlanetscalePanel({ databases, production, deployRequests, rowsRead }: { databases: number; production: number; deployRequests: number; rowsRead: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪐 PlanetScale</h3>
    <div className="text-sm">{production}/{databases} production · {rowsRead.toLocaleString()} reads/24h</div>
    {deployRequests > 0 && <span className="text-xs text-blue-500">{deployRequests} deploy requests open</span>}
  </div>);
}
