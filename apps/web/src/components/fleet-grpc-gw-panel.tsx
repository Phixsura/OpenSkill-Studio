"use client";
export function FleetGrpcGwPanel({ gateways, active, rps, transcoded }: { gateways: number; active: number; rps: number; transcoded: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 gRPC Gateway</h3>
    <div className="text-sm">{active}/{gateways} active · {rps.toLocaleString()} rps · {transcoded.toLocaleString()} transcoded</div>
  </div>);
}
