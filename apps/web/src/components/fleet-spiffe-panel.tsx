"use client";
export function FleetSpiffePanel({ total, withSvid, expired, coveragePct }: { total: number; withSvid: number; expired: number; coveragePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🆔 SPIFFE</h3>
    <div className="text-sm">{withSvid}/{total} with SVID ({coveragePct}%)</div>
    {expired > 0 && <span className="text-xs text-red-500">⚠️ {expired} expired SVIDs</span>}
  </div>);
}
