"use client";
export function FleetHpaEffPanel({ total, responsive, avgScaleTime, effective }: { total: number; responsive: number; avgScaleTime: number; effective: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 HPA Effectiveness</h3>
    <div className="text-sm">{responsive}/{total} responsive · avg {avgScaleTime}s</div>
    {!effective && <span className="text-xs text-yellow-600">⚠️ Slow autoscaling</span>}
  </div>);
}
