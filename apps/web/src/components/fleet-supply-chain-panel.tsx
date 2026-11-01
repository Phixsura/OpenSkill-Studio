"use client";
export function FleetSupplyChainPanel({ total, withSbom, signed, secure }: { total: number; withSbom: number; signed: number; secure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 Supply Chain</h3>
    <div className="text-sm">{withSbom}/{total} SBOM · {signed}/{total} signed</div>
    {!secure && <span className="text-xs text-yellow-600">⚠️ Incomplete supply chain security</span>}
  </div>);
}
