"use client";
export function FleetAiGradCkptPanel({ managers, active, savedGb, overhead, jobs }: { managers: number; active: number; savedGb: number; overhead: number; jobs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 AI Gradient Checkpoint</h3>
    <div className="text-sm">{active}/{managers} active · {savedGb}GB saved · {overhead}% overhead · {jobs} jobs</div>
  </div>);
}
