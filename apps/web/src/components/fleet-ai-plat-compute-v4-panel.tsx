"use client";
export function FleetAiPlatComputeV4Panel({ clusters, active, nodes, gpus, tflops }: { clusters: number; active: number; nodes: number; gpus: number; tflops: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖥️ AI Compute v4</h3>
    <div className="text-sm">{active}/{clusters} active · {nodes.toLocaleString()} nodes · {gpus.toLocaleString()} GPUs · {tflops.toLocaleString()} TFLOPS</div>
  </div>);
}
