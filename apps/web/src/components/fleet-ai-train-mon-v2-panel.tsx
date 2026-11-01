"use client";
export function FleetAiTrainMonV2Panel({ monitors, active, jobs, metrics, alerts }: { monitors: number; active: number; jobs: number; metrics: number; alerts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Training Monitor v2</h3>
    <div className="text-sm">{active}/{monitors} active · {jobs} jobs · {metrics.toLocaleString()} metrics · {alerts} alerts</div>
  </div>);
}
