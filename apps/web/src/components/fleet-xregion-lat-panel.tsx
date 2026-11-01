"use client";
export function FleetXregionLatPanel({ pairs, avgLatency, highLatency, acceptable }: { pairs: number; avgLatency: number; highLatency: number; acceptable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 Cross-Region Latency</h3>
    <div className="text-sm">{avgLatency}ms avg · {pairs} pairs</div>
    {!acceptable && <span className="text-xs text-yellow-600">⚠️ {highLatency} high-latency pairs</span>}
  </div>);
}
