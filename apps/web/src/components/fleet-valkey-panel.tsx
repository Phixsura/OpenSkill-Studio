"use client";
export function FleetValkeyPanel({ nodes, online, keys, memoryGb }: { nodes: number; online: number; keys: number; memoryGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 Valkey</h3>
    <div className="text-sm">{online}/{nodes} online · {keys.toLocaleString()} keys · {memoryGb}GB</div>
  </div>);
}
