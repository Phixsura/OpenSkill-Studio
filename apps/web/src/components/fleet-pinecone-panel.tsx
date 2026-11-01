"use client";
export function FleetPineconePanel({ indexes, ready, vectors, qps }: { indexes: number; ready: number; vectors: number; qps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌲 Pinecone</h3>
    <div className="text-sm">{ready}/{indexes} ready · {vectors.toLocaleString()} vectors · {qps} qps</div>
  </div>);
}
