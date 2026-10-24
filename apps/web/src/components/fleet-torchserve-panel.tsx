"use client";
export function FleetTorchservePanel({ instances, healthy, models, predictions }: { instances: number; healthy: number; models: number; predictions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔥 TorchServe</h3>
    <div className="text-sm">{healthy}/{instances} healthy · {models} models · {predictions.toLocaleString()} pred</div>
  </div>);
}
