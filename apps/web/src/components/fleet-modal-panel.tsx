"use client";
export function FleetModalPanel({ apps, running, gpuHours, functions }: { apps: number; running: number; gpuHours: number; functions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖥️ Modal</h3>
    <div className="text-sm">{running}/{apps} running · {gpuHours}h GPU · {functions} functions</div>
  </div>);
}
