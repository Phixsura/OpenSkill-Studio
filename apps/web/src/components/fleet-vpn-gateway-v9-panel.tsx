"use client";
export function FleetVpnGatewayV9Panel({ tunnels, up }: { tunnels: number; up: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 VPN Gateway v9</h3>
    <div className="text-sm">{tunnels} tunnels · {up} up</div>
  </div>);
}
