"use client";
export function FleetGovernancePanel({ total, enforced, compliancePct, fullyGoverned }: { total: number; enforced: number; compliancePct: number; fullyGoverned: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ Governance</h3>
    <div className={`text-lg font-bold ${fullyGoverned ? "text-green-600" : "text-yellow-600"}`}>{compliancePct}%</div>
    <div className="text-xs text-gray-400">{enforced}/{total} policies enforced</div>
  </div>);
}
