"use client";
export function FleetDirectusPanel({ instances, running, collections, items }: { instances: number; running: number; collections: number; items: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐰 Directus</h3>
    <div className="text-sm">{running}/{instances} running · {collections} collections · {items.toLocaleString()} items</div>
  </div>);
}
