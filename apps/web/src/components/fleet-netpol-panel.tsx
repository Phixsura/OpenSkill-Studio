"use client";
export function FleetNetpolPanel({ total, covered, uncovered, fullCoverage }: { total: number; covered: number; uncovered: number; fullCoverage: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 Network Policies</h3>
    {fullCoverage ? <span className="text-xs text-green-600">✅ All {total} namespaces covered</span>
     : <span className="text-xs text-yellow-600">⚠️ {uncovered}/{total} without network policy</span>}
  </div>);
}
