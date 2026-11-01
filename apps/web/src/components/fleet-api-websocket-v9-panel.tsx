"use client";
export function FleetApiWebsocketV9Panel({ endpoints, connections }: { endpoints: number; connections: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 API WebSocket v9</h3>
    <div className="text-sm">{endpoints} endpoints · {connections.toLocaleString()} connections</div>
  </div>);
}
