"use client";
export function FleetAiWarmPoolPanel({ pools, active, warm, prevented, overhead }: { pools: number; active: number; warm: number; prevented: number; overhead: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔥 AI Warm Pool</h3>
    <div className="text-sm">{active}/{pools} active · {warm} warm · {prevented.toLocaleString()} cold starts prevented · {overhead}% overhead</div>
  </div>);
}
