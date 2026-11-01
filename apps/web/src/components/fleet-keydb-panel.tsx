"use client";
export function FleetKeydbPanel({ nodes, online, keys, opsPerSec }: { nodes: number; online: number; keys: number; opsPerSec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 KeyDB</h3>
    <div className="text-sm">{online}/{nodes} online · {keys.toLocaleString()} keys · {opsPerSec.toLocaleString()} ops/s</div>
  </div>);
}
