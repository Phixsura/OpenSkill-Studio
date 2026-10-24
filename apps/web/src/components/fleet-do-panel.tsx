"use client";
export function FleetDoPanel({ namespaces, activeObjects, storageMb, requests }: { namespaces: number; activeObjects: number; storageMb: number; requests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔶 Durable Objects</h3>
    <div className="text-sm">{namespaces} NS · {activeObjects.toLocaleString()} active · {storageMb}MB · {requests.toLocaleString()} req</div>
  </div>);
}
