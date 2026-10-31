"use client";
export function FleetSoc2Panel({ total, implemented, tested, ready }: { total: number; implemented: number; tested: number; ready: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ SOC2</h3>
    <div className="text-sm">{implemented}/{total} implemented · {tested} tested</div>
    {ready ? <span className="text-xs text-green-600">✅ Audit ready</span>
     : <span className="text-xs text-yellow-600">⚠️ Not audit ready</span>}
  </div>);
}
