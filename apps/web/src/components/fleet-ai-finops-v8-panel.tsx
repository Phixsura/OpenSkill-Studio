"use client";
export function FleetAiFinopsV8Panel({ trackers, active, spend, savings, unitCost }: { trackers: number; active: number; spend: number; savings: number; unitCost: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI FinOps v8</h3>
    <div className="text-sm">{active}/{trackers} active · ${spend.toLocaleString()} · ${savings.toLocaleString()} saved · ${unitCost}/req</div>
  </div>);
}
