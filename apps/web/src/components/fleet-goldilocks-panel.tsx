"use client";
export function FleetGoldilocksPanel({ total, enabled, recommendations }: { total: number; enabled: number; recommendations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐻 Goldilocks</h3>
    <div className="text-sm">{enabled}/{total} enabled · {recommendations} recommendations</div>
  </div>);
}
