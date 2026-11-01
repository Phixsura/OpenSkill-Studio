"use client";
export function FleetAiUnitEconomicsV8Panel({ trackers, active, ltv, cac, ltvCac, payback }: { trackers: number; active: number; ltv: number; cac: number; ltvCac: number; payback: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Unit Economics v8</h3>
    <div className="text-sm">{active}/{trackers} active · LTV ${ltv.toLocaleString()} · CAC ${cac.toLocaleString()} · LTV/CAC {ltvCac}x · {payback}m payback</div>
  </div>);
}
