"use client";
export function FleetOnnxPanel({ instances, running, models, infPerSec }: { instances: number; running: number; models: number; infPerSec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔷 ONNX Runtime</h3>
    <div className="text-sm">{running}/{instances} running · {models} models · {infPerSec.toLocaleString()} inf/s</div>
  </div>);
}
