"use client";
export function FleetAiDataSampPanel({ samplers, active, sampled, strategies, repr }: { samplers: number; active: number; sampled: number; strategies: number; repr: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎲 AI Data Sampler</h3>
    <div className="text-sm">{active}/{samplers} active · {sampled.toLocaleString()} sampled · {strategies} strategies · {repr}% repr</div>
  </div>);
}
