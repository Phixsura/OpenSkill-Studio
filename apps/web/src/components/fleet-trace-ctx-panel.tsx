"use client";
export function FleetTraceCtxPanel({ total, propagating, missing, coveragePct }: { total: number; propagating: number; missing: number; coveragePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 Trace Context</h3>
    <div className="text-sm">{propagating}/{total} propagating ({coveragePct}%)</div>
    {missing > 0 && <span className="text-xs text-yellow-600">⚠️ {missing} missing context</span>}
  </div>);
}
