"use client";
export function FleetTimescaledbPanel({ instances, healthy, chunks, compressionRatio }: { instances: number; healthy: number; chunks: number; compressionRatio: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏰ TimescaleDB</h3>
    <div className="text-sm">{healthy}/{instances} healthy · {chunks.toLocaleString()} chunks · {compressionRatio}x compression</div>
  </div>);
}
