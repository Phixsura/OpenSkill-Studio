"use client";
export function FleetCloudTasksPanel({ queues, active, tasks, successRate }: { queues: number; active: number; tasks: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Cloud Tasks</h3>
    <div className="text-sm">{active}/{queues} active · {tasks.toLocaleString()} tasks · {successRate}%</div>
  </div>);
}
