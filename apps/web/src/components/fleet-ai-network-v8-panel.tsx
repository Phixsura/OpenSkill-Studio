"use client";
export function FleetAiNetworkV8Panel({ systems, active, tbps, latency, regions }: { systems: number; active: number; tbps: number; latency: number; regions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 AI Network v8</h3>
    <div className="text-sm">{active}/{systems} active · {tbps}Tbps · {latency}ms · {regions} regions</div>
  </div>);
}
