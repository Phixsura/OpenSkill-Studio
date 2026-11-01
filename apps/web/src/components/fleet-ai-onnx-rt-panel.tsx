"use client";
export function FleetAiOnnxRtPanel({ runtimes, active, models, inferences, speedup }: { runtimes: number; active: number; models: number; inferences: number; speedup: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ AI ONNX Runtime</h3>
    <div className="text-sm">{active}/{runtimes} active · {models} models · {inferences.toLocaleString()} inf · {speedup}x speed</div>
  </div>);
}
