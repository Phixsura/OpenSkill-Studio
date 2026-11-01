"use client";
export function FleetCatMaturityPanel({ total, fullyCataloged, partial, maturityPct, mature }: { total: number; fullyCataloged: number; partial: number; maturityPct: number; mature: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📚 Catalog Maturity</h3>
    <div className={`text-lg font-bold ${mature ? "text-green-600" : "text-yellow-600"}`}>{maturityPct}%</div>
    <div className="text-xs text-gray-400">{fullyCataloged}/{total} complete · {partial} partial</div>
  </div>);
}
