"use client";
export function FleetAiAutoEvalPanel({ evaluators, active, evals, correlation, cost }: { evaluators: number; active: number; evals: number; correlation: number; cost: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 AI Auto Eval</h3>
    <div className="text-sm">{active}/{evaluators} active · {evals.toLocaleString()} evals · {correlation} correlation · ${cost}/eval</div>
  </div>);
}
