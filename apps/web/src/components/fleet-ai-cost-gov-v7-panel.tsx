"use client";
export function FleetAiCostGovV7Panel({ systems, active, budgets, spend, within }: { systems: number; active: number; budgets: number; spend: number; within: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Cost Governance v7</h3>
    <div className="text-sm">{active}/{systems} active · {budgets} budgets · ${spend.toLocaleString()} · {within ? "✅ within" : "⚠️ over"}</div>
  </div>);
}
