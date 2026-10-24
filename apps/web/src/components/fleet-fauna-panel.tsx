"use client";
export function FleetFaunaPanel({ databases, active, collections, readOps }: { databases: number; active: number; collections: number; readOps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌿 Fauna</h3>
    <div className="text-sm">{active}/{databases} active · {collections} collections · {readOps.toLocaleString()} reads</div>
  </div>);
}
