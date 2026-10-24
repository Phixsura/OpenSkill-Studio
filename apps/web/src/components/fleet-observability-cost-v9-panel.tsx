"use client";
export function FleetObservabilityCostV9Panel({ sources, cost }: { sources: number; cost: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Observability Cost v9</h3>
    <div className="text-sm">{sources} sources · ${cost.toLocaleString()}/mo</div>
  </div>);
}
