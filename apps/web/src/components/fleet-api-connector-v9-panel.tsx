"use client";
export function FleetApiConnectorV9Panel({ connectors, connected }: { connectors: number; connected: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 API Connector v9</h3>
    <div className="text-sm">{connectors} connectors · {connected} connected</div>
  </div>);
}
