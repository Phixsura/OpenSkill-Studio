"use client";
export function FleetAiModelParPanel({ configs, active, gpus, tp, pp, efficiency }: { configs: number; active: number; gpus: number; tp: number; pp: number; efficiency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 AI Model Parallelism</h3>
    <div className="text-sm">{active}/{configs} active · {gpus} GPUs · TP{tp} PP{pp} · {efficiency}% efficient</div>
  </div>);
}
