"use client";
export function FleetAiFinopsV7Panel({ trackers, active, spend, savings, costPerReq, roi }: { trackers: number; active: number; spend: number; savings: number; costPerReq: number; roi: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI FinOps v7</h3>
    <div className="text-sm">{active}/{trackers} active · ${spend.toLocaleString()} · ${savings.toLocaleString()} saved · {roi}% ROI</div>
  </div>);
}
