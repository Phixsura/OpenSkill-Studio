"use client";
export function FleetScaleHistPanel({ total, scaleUps, scaleDowns, ratio }: { total: number; scaleUps: number; scaleDowns: number; ratio: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Scaling History</h3>
    <div className="text-sm">⬆️ {scaleUps} · ⬇️ {scaleDowns} · ratio {ratio}x</div>
  </div>);
}
