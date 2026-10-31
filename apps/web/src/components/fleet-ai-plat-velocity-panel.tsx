"use client";
export function FleetAiPlatVelocityPanel({ trackers, active, commits, prs, cycleTime }: { trackers: number; active: number; commits: number; prs: number; cycleTime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Platform Velocity</h3>
    <div className="text-sm">{active}/{trackers} active · {commits} commits/wk · {prs} PRs/wk · {cycleTime}h cycle</div>
  </div>);
}
