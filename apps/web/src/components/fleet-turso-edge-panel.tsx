"use client";
export function FleetTursoEdgePanel({ groups, primary, replicas, locations }: { groups: number; primary: number; replicas: number; locations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 Turso Edge</h3>
    <div className="text-sm">{groups} groups · {primary}P/{replicas}R · {locations} locations</div>
  </div>);
}
