"use client";
export function FleetAiLogAggPanel({ aggregators, active, logs, storageGb, sources }: { aggregators: number; active: number; logs: number; storageGb: number; sources: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Log Aggregator</h3>
    <div className="text-sm">{active}/{aggregators} active · {logs.toLocaleString()} logs · {storageGb}GB · {sources} sources</div>
  </div>);
}
