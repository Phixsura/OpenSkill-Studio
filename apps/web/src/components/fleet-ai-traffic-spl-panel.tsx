"use client";
export function FleetAiTrafficSplPanel({ splitters, active, splits, requests, variants }: { splitters: number; active: number; splits: number; requests: number; variants: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 AI Traffic Split</h3>
    <div className="text-sm">{active}/{splitters} active · {splits} splits · {requests.toLocaleString()} req · {variants} variants</div>
  </div>);
}
