"use client";
export function FleetAiComputeV8Panel({ clusters, active, nodes, gpus, tflops, utilization }: { clusters: number; active: number; nodes: number; gpus: number; tflops: number; utilization: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖥️ AI Compute v8</h3>
    <div className="text-sm">{active}/{clusters} active · {nodes.toLocaleString()} nodes · {gpus.toLocaleString()} GPUs · {utilization}%</div>
  </div>);
}
