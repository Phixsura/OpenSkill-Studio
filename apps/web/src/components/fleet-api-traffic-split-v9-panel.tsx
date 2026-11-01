"use client";
export function FleetApiTrafficSplitV9Panel({ splits, canaryPct }: { splits: number; canaryPct: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 Traffic Split v9</h3>
    <div className="text-sm">{splits} splits · {canaryPct}% canary</div>
  </div>);
}
