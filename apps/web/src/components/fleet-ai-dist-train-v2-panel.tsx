"use client";
export function FleetAiDistTrainV2Panel({ trainers, active, nodes, gpus, efficiency }: { trainers: number; active: number; nodes: number; gpus: number; efficiency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏋️ AI Distributed Training v2</h3>
    <div className="text-sm">{active}/{trainers} active · {nodes} nodes · {gpus} GPUs · {efficiency}% efficiency</div>
  </div>);
}
