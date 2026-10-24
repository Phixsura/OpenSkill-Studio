"use client";
export function FleetAtlantisPanel({ total, enabled, plans, applies }: { total: number; enabled: number; plans: number; applies: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏛️ Atlantis</h3>
    <div className="text-sm">{enabled}/{total} enabled · {plans} plans · {applies} applies/24h</div>
  </div>);
}
