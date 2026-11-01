"use client";
export function FleetAiFinopsV6Panel({ trackers, active, spend, savings, costPerReq }: { trackers: number; active: number; spend: number; savings: number; costPerReq: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI FinOps v6</h3>
    <div className="text-sm">{active}/{trackers} active · ${spend.toLocaleString()} · ${savings.toLocaleString()} saved · ${costPerReq}/req</div>
  </div>);
}
