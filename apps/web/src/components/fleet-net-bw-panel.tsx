"use client";
export function FleetNetBwPanel({ totalGbps, usedGbps, utilPct, saturated }: { totalGbps: number; usedGbps: number; utilPct: number; saturated: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 Network Bandwidth</h3>
    <div className="text-sm">{usedGbps}/{totalGbps} Gbps ({utilPct}%)</div>
    {saturated && <span className="text-xs text-red-500">⚠️ Near saturation</span>}
  </div>);
}
