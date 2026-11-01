"use client";
export function FleetTogetherPanel({ models, deployed, inferences, gpuHours }: { models: number; deployed: number; inferences: number; gpuHours: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤝 Together AI</h3>
    <div className="text-sm">{deployed}/{models} deployed · {inferences.toLocaleString()} inferences · {gpuHours}h GPU</div>
  </div>);
}
