"use client";
export function FleetAiSpotInstPanel({ managers, active, instances, savings, interruptions }: { managers: number; active: number; instances: number; savings: number; interruptions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Spot Instances</h3>
    <div className="text-sm">{active}/{managers} active · {instances} instances · {savings}% savings · {interruptions} interrupts</div>
  </div>);
}
