"use client";
export function FleetHfPanel({ spaces, running, models, inferences }: { spaces: number; running: number; models: number; inferences: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤗 Hugging Face</h3>
    <div className="text-sm">{running}/{spaces} running · {models} models · {inferences.toLocaleString()} inferences</div>
  </div>);
}
