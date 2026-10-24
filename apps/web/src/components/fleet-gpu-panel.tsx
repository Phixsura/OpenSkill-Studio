"use client";
export function FleetGpuPanel({ total, active, idle, avgUtil, wasteful }: { total: number; active: number; idle: number; avgUtil: number; wasteful: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎮 GPU Fleet</h3>
    <div className="text-sm">{active} active · {idle} idle · {avgUtil}% avg</div>
    {wasteful && <span className="text-xs text-yellow-600">💸 Low GPU utilization</span>}
  </div>);
}
