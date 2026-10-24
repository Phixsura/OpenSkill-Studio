"use client";
export function FleetSplitIoPanel({ total, active, withMetrics, treatments }: { total: number; active: number; withMetrics: number; treatments: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔬 Split.io</h3>
    <div className="text-sm">{active}/{total} active · {withMetrics} with metrics · {treatments} treatments</div>
  </div>);
}
