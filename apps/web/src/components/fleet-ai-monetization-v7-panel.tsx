"use client";
export function FleetAiMonetizationV7Panel({ trackers, active, mrr, arpu, ltv, payback }: { trackers: number; active: number; mrr: number; arpu: number; ltv: number; payback: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Monetization v7</h3>
    <div className="text-sm">{active}/{trackers} active · ${mrr.toLocaleString()} MRR · ${arpu} ARPU · ${ltv.toLocaleString()} LTV · {payback}m payback</div>
  </div>);
}
