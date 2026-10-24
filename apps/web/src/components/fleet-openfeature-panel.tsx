"use client";
export function FleetOpenfeaturePanel({ total, active, evaluations }: { total: number; active: number; evaluations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚩 OpenFeature</h3>
    <div className="text-sm">{active}/{total} providers · {evaluations.toLocaleString()} evals/24h</div>
  </div>);
}
