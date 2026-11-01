"use client";
export function FleetAiTaskSchedPanel({ schedulers, active, tasks, executions, failures }: { schedulers: number; active: number; tasks: number; executions: number; failures: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏰ AI Task Scheduler</h3>
    <div className="text-sm">{active}/{schedulers} active · {tasks} tasks · {executions.toLocaleString()} exec · {failures} failures</div>
  </div>);
}
