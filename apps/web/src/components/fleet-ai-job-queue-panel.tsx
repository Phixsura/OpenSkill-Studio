"use client";
export function FleetAiJobQueuePanel({ queues, active, pending, processing, completed, workers }: { queues: number; active: number; pending: number; processing: number; completed: number; workers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Job Queue</h3>
    <div className="text-sm">{active}/{queues} active · {pending} pending · {processing} processing · {completed.toLocaleString()} done · {workers} workers</div>
  </div>);
}
