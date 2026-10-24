"use client";
export function FleetRespSizePanel({ total, avgKb, largeResponses, optimized }: { total: number; avgKb: number; largeResponses: number; optimized: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Response Size</h3>
    <div className="text-sm">avg {avgKb}KB · {total} endpoints</div>
    {!optimized && <span className="text-xs text-yellow-600">⚠️ {largeResponses} oversized responses</span>}
  </div>);
}
