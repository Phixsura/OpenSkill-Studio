"use client";
export function FleetAiOptStatePanel({ managers, active, states, storageGb, restorations }: { managers: number; active: number; states: number; storageGb: number; restorations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 AI Optimizer State</h3>
    <div className="text-sm">{active}/{managers} active · {states.toLocaleString()} states · {storageGb}GB · {restorations} restorations</div>
  </div>);
}
