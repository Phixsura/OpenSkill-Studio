"use client";
export function FleetAiEarlyStopPanel({ managers, active, jobs, stopped, saved }: { managers: number; active: number; jobs: number; stopped: number; saved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛑 AI Early Stopping</h3>
    <div className="text-sm">{active}/{managers} active · {jobs} jobs · {stopped} stopped early · {saved}% compute saved</div>
  </div>);
}
