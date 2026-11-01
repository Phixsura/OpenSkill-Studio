"use client";
export function FleetDataLocPanel({ total, compliant, violations, fullyCompliant }: { total: number; compliant: number; violations: number; fullyCompliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📍 Data Locality</h3>
    {fullyCompliant ? <span className="text-xs text-green-600">✅ All {total} compliant</span>
     : <span className="text-xs text-red-500">⚠️ {violations} residency violations</span>}
  </div>);
}
