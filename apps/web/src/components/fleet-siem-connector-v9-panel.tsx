"use client";
export function FleetSiemConnectorV9Panel({ connectors, events }: { connectors: number; events: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ SIEM Connector v9</h3>
    <div className="text-sm">{connectors} connectors · {events.toLocaleString()} events</div>
  </div>);
}
