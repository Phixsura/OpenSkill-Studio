"use client";
export function FleetAiTensorPanel({ clusters, active, tflops, jobs, utilization }: { clusters: number; active: number; tflops: number; jobs: number; utilization: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔢 AI Tensor Compute</h3>
    <div className="text-sm">{active}/{clusters} active · {tflops.toLocaleString()} TFLOPS · {jobs.toLocaleString()} jobs · {utilization}% util</div>
  </div>);
}
