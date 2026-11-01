"use client";
export function FleetGpuClusterV9Panel({ nodes, gpus }: { nodes: number; gpus: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎮 GPU Cluster v9</h3>
    <div className="text-sm">{nodes} nodes · {gpus} GPUs</div>
  </div>);
}
