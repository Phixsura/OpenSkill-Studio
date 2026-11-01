"use client";
export function FleetAwsBatchPanel({ queues, active, submitted, running, succeeded }: { queues: number; active: number; submitted: number; running: number; succeeded: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ AWS Batch</h3>
    <div className="text-sm">{active}/{queues} active · {submitted} submitted · {running} running · {succeeded} succeeded</div>
  </div>);
}
