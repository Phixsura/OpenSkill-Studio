"use client";
export function FleetEcsPanel({ services, active, runningTasks, desiredTasks, stable }: { services: number; active: number; runningTasks: number; desiredTasks: number; stable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐳 ECS</h3>
    <div className="text-sm">{active}/{services} active · {runningTasks}/{desiredTasks} tasks</div>
    {!stable && <span className="text-xs text-yellow-600">⚠️ Scaling in progress</span>}
  </div>);
}
