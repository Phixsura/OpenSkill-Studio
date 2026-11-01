"use client";
export function FleetAiCostOptV3Panel({ optimizers, active, spend, savings, recs, implemented, roi }: { optimizers: number; active: number; spend: number; savings: number; recs: number; implemented: number; roi: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💸 AI Cost Optimizer v3</h3>
    <div className="text-sm">{active}/{optimizers} active · ${spend.toLocaleString()} spend · ${savings.toLocaleString()} saved · {implemented}/{recs} recs · {roi}% ROI</div>
  </div>);
}
