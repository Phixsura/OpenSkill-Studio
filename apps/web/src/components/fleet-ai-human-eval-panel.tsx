"use client";
export function FleetAiHumanEvalPanel({ systems, active, evals, evaluators, agreement }: { systems: number; active: number; evals: number; evaluators: number; agreement: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👤 AI Human Eval</h3>
    <div className="text-sm">{active}/{systems} active · {evals.toLocaleString()} evals · {evaluators} evaluators · {agreement}% agreement</div>
  </div>);
}
