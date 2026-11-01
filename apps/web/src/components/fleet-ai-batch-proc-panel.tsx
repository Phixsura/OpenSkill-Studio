"use client";
export function FleetAiBatchProcPanel({ processors, active, jobs, items, throughput }: { processors: number; active: number; jobs: number; items: number; throughput: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Batch Processor</h3>
    <div className="text-sm">{active}/{processors} active · {jobs.toLocaleString()} jobs · {items.toLocaleString()} items · {throughput.toLocaleString()}/s</div>
  </div>);
}
