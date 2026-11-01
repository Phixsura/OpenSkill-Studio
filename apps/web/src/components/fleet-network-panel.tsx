"use client";
export function FleetNetworkPanel({ rxMbps, txMbps, totalMbps }: { rxMbps: number; txMbps: number; totalMbps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 Fleet Network</h3>
    <div className="text-sm">↓ {rxMbps} Mbps · ↑ {txMbps} Mbps · Total {totalMbps} Mbps</div>
  </div>);
}
