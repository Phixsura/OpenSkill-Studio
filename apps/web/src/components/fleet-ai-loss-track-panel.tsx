"use client";
export function FleetAiLossTrackPanel({ trackers, active, jobs, loss, converged }: { trackers: number; active: number; jobs: number; loss: number; converged: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📉 AI Loss Tracker</h3>
    <div className="text-sm">{active}/{trackers} active · {jobs} jobs · loss {loss} · {converged} converged</div>
  </div>);
}
