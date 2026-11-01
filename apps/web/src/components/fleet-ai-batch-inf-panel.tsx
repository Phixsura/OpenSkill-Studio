"use client";
export function FleetAiBatchInfPanel({ jobs, running, completed, samples, latency }: { jobs: number; running: number; completed: number; samples: number; latency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Batch Inference</h3>
    <div className="text-sm">{running} running · {completed} done · {samples.toLocaleString()} samples · {latency}ms avg</div>
  </div>);
}
