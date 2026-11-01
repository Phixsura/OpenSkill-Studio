"use client";
export function FleetAiGpuClusterPanel({ clusters, active, gpus, utilized, utilization, tflops }: { clusters: number; active: number; gpus: number; utilized: number; utilization: number; tflops: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖥️ AI GPU Cluster</h3>
    <div className="text-sm">{active}/{clusters} active · {utilized}/{gpus} GPUs ({utilization}%) · {tflops.toLocaleString()} TFLOPS</div>
  </div>);
}
