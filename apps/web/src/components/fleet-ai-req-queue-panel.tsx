"use client";
export function FleetAiReqQueuePanel({ queues, active, depth, throughput, avgWait }: { queues: number; active: number; depth: number; throughput: number; avgWait: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📬 AI Request Queue</h3>
    <div className="text-sm">{active}/{queues} active · {depth} depth · {throughput.toLocaleString()} RPS · {avgWait}ms wait</div>
  </div>);
}
