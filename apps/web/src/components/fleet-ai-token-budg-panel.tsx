"use client";
export function FleetAiTokenBudgPanel({ budgets, active, allocated, used, utilization, cost }: { budgets: number; active: number; allocated: number; used: number; utilization: number; cost: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Token Budget</h3>
    <div className="text-sm">{active}/{budgets} active · {utilization}% used · ${cost.toLocaleString()}</div>
  </div>);
}
