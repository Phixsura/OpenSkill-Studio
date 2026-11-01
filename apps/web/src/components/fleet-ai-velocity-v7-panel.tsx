"use client";
export function FleetAiVelocityV7Panel({ trackers, active, commits, prs, cycle, features }: { trackers: number; active: number; commits: number; prs: number; cycle: number; features: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Velocity v7</h3>
    <div className="text-sm">{active}/{trackers} active · {commits} commits/wk · {prs} PRs · {cycle}h cycle · {features} features</div>
  </div>);
}
