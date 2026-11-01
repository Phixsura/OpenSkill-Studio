"use client";
export function FleetAiGpuSchedPanel({ schedulers, active, gpus, queued, utilization }: { schedulers: number; active: number; gpus: number; queued: number; utilization: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖥️ AI GPU Scheduler</h3>
    <div className="text-sm">{active}/{schedulers} active · {gpus} GPUs · {queued} queued · {utilization}% util</div>
  </div>);
}
