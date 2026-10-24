"use client";
export function FleetDepLicensePanel({ total, approved, copyleft, unknown, compliant }: { total: number; approved: number; copyleft: number; unknown: number; compliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 Dep Licenses</h3>
    {compliant ? <span className="text-xs text-green-600">✅ All {total} deps license-compliant</span>
     : <span className="text-xs text-yellow-600">⚠️ {copyleft} copyleft · {unknown} unknown</span>}
  </div>);
}
