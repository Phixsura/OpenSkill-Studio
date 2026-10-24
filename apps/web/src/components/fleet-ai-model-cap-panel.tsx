"use client";
export function FleetAiModelCapPanel({ planners, active, models, maxRps, utilization }: { planners: number; active: number; models: number; maxRps: number; utilization: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Model Capacity</h3>
    <div className="text-sm">{active}/{planners} active · {models} models · {maxRps.toLocaleString()} max RPS · {utilization}% util</div>
  </div>);
}
