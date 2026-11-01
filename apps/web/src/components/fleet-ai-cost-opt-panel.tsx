"use client";
export function FleetAiCostOptPanel({ optimizers, active, spend, savings, savingsPct }: { optimizers: number; active: number; spend: number; savings: number; savingsPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💸 AI Cost Optimizer</h3>
    <div className="text-sm">{active}/{optimizers} active · ${spend.toLocaleString()}/mo · ${savings.toLocaleString()} saved ({savingsPct}%)</div>
  </div>);
}
