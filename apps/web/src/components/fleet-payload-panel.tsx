"use client";
export function FleetPayloadPanel({ instances, running, collections, documents }: { instances: number; running: number; collections: number; documents: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Payload</h3>
    <div className="text-sm">{running}/{instances} running · {collections} collections · {documents.toLocaleString()} docs</div>
  </div>);
}
