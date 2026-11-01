"use client";
export function FleetApiGatewayHealthV9Panel({ gateways, rps }: { gateways: number; rps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚪 Gateway Health v9</h3>
    <div className="text-sm">{gateways} gateways · {rps.toLocaleString()} rps</div>
  </div>);
}
