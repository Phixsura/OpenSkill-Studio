"use client";
export function FleetTfservingPanel({ instances, serving, models, batchesPerSec }: { instances: number; serving: number; models: number; batchesPerSec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧠 TF Serving</h3>
    <div className="text-sm">{serving}/{instances} serving · {models} models · {batchesPerSec.toLocaleString()} batch/s</div>
  </div>);
}
