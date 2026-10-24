"use client";
export function FleetKvPanel({ namespaces, keys, reads, writes }: { namespaces: number; keys: number; reads: number; writes: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 KV Store</h3>
    <div className="text-sm">{namespaces} NS · {keys.toLocaleString()} keys · {reads.toLocaleString()} reads</div>
  </div>);
}
