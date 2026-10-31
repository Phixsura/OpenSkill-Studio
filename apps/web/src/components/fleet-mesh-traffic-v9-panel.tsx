"use client";
export function FleetMeshTrafficV9Panel({ splits, rps }: { splits: number; rps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ Mesh Traffic v9</h3>
    <div className="text-sm">{splits} splits · {rps.toLocaleString()} rps</div>
  </div>);
}
