"use client";
export function FleetApiGovernanceV9Panel({ apis, compliant }: { apis: number; compliant: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏛️ API Governance v9</h3>
    <div className="text-sm">{apis} APIs · {compliant} compliant</div>
  </div>);
}
