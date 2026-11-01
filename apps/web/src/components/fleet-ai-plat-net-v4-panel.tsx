"use client";
export function FleetAiPlatNetV4Panel({ systems, active, bandwidth, latency }: { systems: number; active: number; bandwidth: number; latency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 AI Network v4</h3>
    <div className="text-sm">{active}/{systems} active · {bandwidth}Gbps · {latency}ms latency</div>
  </div>);
}
