"use client";
export function FleetAiBatchSchedPanel({ schedulers, active, batches, items, utilization }: { schedulers: number; active: number; batches: number; items: number; utilization: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Batch Scheduler</h3>
    <div className="text-sm">{active}/{schedulers} active · {batches} batches · {items.toLocaleString()} items · {utilization}% util</div>
  </div>);
}
