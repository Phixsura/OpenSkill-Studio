"use client";
export function FleetHedgingPanel({ totalHedged, saved, effectivenessPct, worthwhile }: { totalHedged: number; saved: number; effectivenessPct: number; worthwhile: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 Request Hedging</h3>
    <div className="text-sm">{totalHedged.toLocaleString()} hedged · {saved} saved ({effectivenessPct}%)</div>
    {worthwhile && <span className="text-xs text-green-600">✅ Effective</span>}
  </div>);
}
