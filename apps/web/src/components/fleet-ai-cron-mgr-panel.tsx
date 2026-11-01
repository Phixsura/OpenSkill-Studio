"use client";
export function FleetAiCronMgrPanel({ managers, active, jobs, runs, missed }: { managers: number; active: number; jobs: number; runs: number; missed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏲️ AI Cron Manager</h3>
    <div className="text-sm">{active}/{managers} active · {jobs} jobs · {runs.toLocaleString()} runs · {missed} missed</div>
  </div>);
}
