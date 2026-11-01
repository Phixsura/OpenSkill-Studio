"use client";
export function FleetAiRlhfPanel({ pipelines, active, comparisons, rewardAcc, ppoSteps }: { pipelines: number; active: number; comparisons: number; rewardAcc: number; ppoSteps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 AI RLHF</h3>
    <div className="text-sm">{active}/{pipelines} active · {comparisons.toLocaleString()} pairs · {rewardAcc}% RM acc · {ppoSteps.toLocaleString()} PPO steps</div>
  </div>);
}
