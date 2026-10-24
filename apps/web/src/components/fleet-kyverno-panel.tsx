"use client";
export function FleetKyvernoPanel({ total, enforcing, audit, violations, compliant }: { total: number; enforcing: number; audit: number; violations: number; compliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 Kyverno</h3>
    <div className="text-sm">{enforcing} enforce · {audit} audit · {violations} violations</div>
    {!compliant && <span className="text-xs text-yellow-600">⚠️ Policy violations</span>}
  </div>);
}
