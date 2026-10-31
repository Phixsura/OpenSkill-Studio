"use client";
export function FleetGatekeeperPanel({ total, enforced, auditOnly, violations, clean }: { total: number; enforced: number; auditOnly: number; violations: number; clean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚧 Gatekeeper</h3>
    <div className="text-sm">{enforced} enforced · {auditOnly} audit</div>
    {!clean && <span className="text-xs text-yellow-600">⚠️ {violations} violations</span>}
  </div>);
}
