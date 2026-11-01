"use client";
export function FleetAiCapacityV5Panel({ planners, active, gpus, headroom, forecast }: { planners: number; active: number; gpus: number; headroom: number; forecast: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Capacity v5</h3>
    <div className="text-sm">{active}/{planners} active · {gpus.toLocaleString()} GPUs · {headroom}% headroom · {forecast}d forecast</div>
  </div>);
}
