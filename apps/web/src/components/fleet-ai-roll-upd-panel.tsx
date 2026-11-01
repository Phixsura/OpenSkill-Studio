"use client";
export function FleetAiRollUpdPanel({ updaters, active, updates, instances, rollbacks }: { updaters: number; active: number; updates: number; instances: number; rollbacks: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI Rolling Update</h3>
    <div className="text-sm">{active}/{updaters} active · {updates} updates · {instances} instances · {rollbacks} rollbacks</div>
  </div>);
}
