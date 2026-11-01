"use client";
export function FleetRbacAuditPanel({ total, overprivileged, compliant }: { total: number; overprivileged: number; compliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👤 RBAC Audit</h3>
    {compliant ? <span className="text-xs text-green-600">✅ All {total} accounts compliant</span>
     : <span className="text-xs text-red-500">⚠️ {overprivileged} overprivileged accounts</span>}
  </div>);
}
