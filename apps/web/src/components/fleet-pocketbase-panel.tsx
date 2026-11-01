"use client";
export function FleetPocketbasePanel({ instances, running, collections, records }: { instances: number; running: number; collections: number; records: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 PocketBase</h3>
    <div className="text-sm">{running}/{instances} running · {collections} collections · {records.toLocaleString()} records</div>
  </div>);
}
