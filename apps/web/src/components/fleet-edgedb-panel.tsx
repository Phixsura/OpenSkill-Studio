"use client";
export function FleetEdgedbPanel({ instances, available, branches, types }: { instances: number; available: number; branches: number; types: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔶 EdgeDB</h3>
    <div className="text-sm">{available}/{instances} available · {branches} branches · {types} types</div>
  </div>);
}
