"use client";
export function FleetTursoPanel({ databases, replicas, totalRows, locations }: { databases: number; replicas: number; totalRows: number; locations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 Turso</h3>
    <div className="text-sm">{databases} DBs · {replicas} replicas · {totalRows.toLocaleString()} rows · {locations} locations</div>
  </div>);
}
