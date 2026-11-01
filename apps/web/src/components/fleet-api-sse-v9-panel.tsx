"use client";
export function FleetApiSseV9Panel({ streams, connections }: { streams: number; connections: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 API SSE v9</h3>
    <div className="text-sm">{streams} streams · {connections.toLocaleString()} connections</div>
  </div>);
}
