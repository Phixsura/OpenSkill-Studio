"use client";
export function FleetAiModelWarmPanel({ managers, active, warmed, prevented, warmup }: { managers: number; active: number; warmed: number; prevented: number; warmup: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔥 AI Model Warm-Up</h3>
    <div className="text-sm">{active}/{managers} active · {warmed} warmed · {prevented.toLocaleString()} cold starts prevented · {warmup}s</div>
  </div>);
}
