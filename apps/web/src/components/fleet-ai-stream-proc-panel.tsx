"use client";
export function FleetAiStreamProcPanel({ processors, active, eps, partitions, lag }: { processors: number; active: number; eps: number; partitions: number; lag: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌊 AI Stream Processor</h3>
    <div className="text-sm">{active}/{processors} active · {eps.toLocaleString()} EPS · {partitions} partitions · lag {lag}</div>
  </div>);
}
