"use client";
export function FleetQdrantPanel({ collections, green, totalPoints }: { collections: number; green: number; totalPoints: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔷 Qdrant</h3>
    <div className="text-sm">{green}/{collections} green · {totalPoints.toLocaleString()} points</div>
  </div>);
}
