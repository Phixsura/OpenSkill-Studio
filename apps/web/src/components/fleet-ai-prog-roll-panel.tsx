"use client";
export function FleetAiProgRollPanel({ rollouts, active, currentPct, stagesDone, totalStages }: { rollouts: number; active: number; currentPct: number; stagesDone: number; totalStages: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Progressive Rollout</h3>
    <div className="text-sm">{active}/{rollouts} active · {currentPct}% rolled · {stagesDone}/{totalStages} stages</div>
  </div>);
}
