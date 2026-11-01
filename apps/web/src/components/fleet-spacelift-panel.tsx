"use client";
export function FleetSpaceliftPanel({ total, tracked, drifted, policies }: { total: number; tracked: number; drifted: number; policies: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Spacelift</h3>
    <div className="text-sm">{tracked}/{total} tracked · {policies} policies</div>
    {drifted > 0 && <span className="text-xs text-yellow-600">⚠️ {drifted} drifted</span>}
  </div>);
}
