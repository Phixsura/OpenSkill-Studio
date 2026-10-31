"use client";
export function FleetAiTrainSchedPanel({ schedulers, active, queued, running, completed, avgWait }: { schedulers: number; active: number; queued: number; running: number; completed: number; avgWait: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📅 AI Training Scheduler</h3>
    <div className="text-sm">{active}/{schedulers} active · {queued} queued · {running} running · {completed} done · {avgWait}m wait</div>
  </div>);
}
