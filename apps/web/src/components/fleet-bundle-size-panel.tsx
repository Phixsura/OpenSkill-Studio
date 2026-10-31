"use client";
export function FleetBundleSizePanel({ totalKb, bundles, large, optimized }: { totalKb: number; bundles: number; large: number; optimized: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Bundle Size</h3>
    <div className="text-sm">{totalKb}KB total · {bundles} bundles</div>
    {!optimized && <span className="text-xs text-yellow-600">⚠️ {large} oversized bundles</span>}
  </div>);
}
