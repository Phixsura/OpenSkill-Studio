"use client";
export function FleetSparkPanel({ clusters, running, executors, activeJobs }: { clusters: number; running: number; executors: number; activeJobs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Spark</h3>
    <div className="text-sm">{running}/{clusters} running · {executors} executors · {activeJobs} jobs</div>
  </div>);
}
