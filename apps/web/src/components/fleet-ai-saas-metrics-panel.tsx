"use client";
export function FleetAiSaasMetricsPanel({ trackers, active, arr, ltv, cac, ltvCac }: { trackers: number; active: number; arr: number; ltv: number; cac: number; ltvCac: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💼 AI SaaS Metrics</h3>
    <div className="text-sm">{active}/{trackers} active · ${arr.toLocaleString()} ARR · LTV ${ltv.toLocaleString()} · CAC ${cac.toLocaleString()} · LTV/CAC {ltvCac}x</div>
  </div>);
}
