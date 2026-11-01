"use client";
export function FleetAiWorkerPoolPanel({ pools, active, workers, busy, idle, utilization }: { pools: number; active: number; workers: number; busy: number; idle: number; utilization: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👷 AI Worker Pool</h3>
    <div className="text-sm">{active}/{pools} active · {busy}/{workers} busy · {idle} idle · {utilization}%</div>
  </div>);
}
