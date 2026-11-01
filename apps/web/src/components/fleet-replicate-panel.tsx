"use client";
export function FleetReplicatePanel({ models, active, predictions, avgRunSec }: { models: number; active: number; predictions: number; avgRunSec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Replicate</h3>
    <div className="text-sm">{active}/{models} active · {predictions.toLocaleString()} predictions · {avgRunSec}s avg</div>
  </div>);
}
