"use client";
export function FleetAiCapPlanV2Panel({ planners, active, forecastDays, accuracy, savings }: { planners: number; active: number; forecastDays: number; accuracy: number; savings: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Capacity Planner v2</h3>
    <div className="text-sm">{active}/{planners} active · {forecastDays}d forecast · {accuracy}% acc · {savings}% savings</div>
  </div>);
}
