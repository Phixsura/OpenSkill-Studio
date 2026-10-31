"use client";
export function FleetCloudGovernanceV9Panel({ rules, violations }: { rules: number; violations: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏛️ Cloud Governance v9</h3>
    <div className="text-sm">{rules} rules · {violations} violations</div>
  </div>);
}
