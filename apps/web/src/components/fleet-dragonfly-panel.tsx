"use client";
export function FleetDragonflyPanel({ instances, running, memoryGb, opsPerSec }: { instances: number; running: number; memoryGb: number; opsPerSec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐉 Dragonfly</h3>
    <div className="text-sm">{running}/{instances} running · {memoryGb}GB · {opsPerSec.toLocaleString()} ops/s</div>
  </div>);
}
