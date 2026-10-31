"use client";
export function FleetAiErrBudgetPanel({ budgets, active, remaining, burnRate, slos }: { budgets: number; active: number; remaining: number; burnRate: number; slos: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Error Budget</h3>
    <div className="text-sm">{active}/{budgets} active · {remaining}% remaining · {burnRate}x burn · {slos} SLOs</div>
  </div>);
}
