"use client";
export function FleetTriggerdevPanel({ projects, active, runs, tasks }: { projects: number; active: number; runs: number; tasks: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Trigger.dev</h3>
    <div className="text-sm">{active}/{projects} active · {runs.toLocaleString()} runs · {tasks} tasks</div>
  </div>);
}
