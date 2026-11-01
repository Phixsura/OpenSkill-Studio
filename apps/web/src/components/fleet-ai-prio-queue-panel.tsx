"use client";
export function FleetAiPrioQueuePanel({ queues, active, levels, promoted, total }: { queues: number; active: number; levels: number; promoted: number; total: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Priority Queue</h3>
    <div className="text-sm">{active}/{queues} active · {levels} levels · {promoted.toLocaleString()} promoted · {total.toLocaleString()} total</div>
  </div>);
}
