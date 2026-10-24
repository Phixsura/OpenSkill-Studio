"use client";
export function FleetAiCapacityPanel({ plans, active, forecastDays, utilization, headroom }: { plans: number; active: number; forecastDays: number; utilization: number; headroom: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Capacity Planning</h3>
    <div className="text-sm">{active}/{plans} active · {forecastDays}d forecast · {utilization}% util · {headroom}% headroom</div>
  </div>);
}
