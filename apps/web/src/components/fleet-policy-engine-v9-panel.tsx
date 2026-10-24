"use client";
export function FleetPolicyEngineV9Panel({ policies, violations }: { policies: number; violations: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Policy Engine v9</h3>
    <div className="text-sm">{policies} policies · {violations} violations</div>
  </div>);
}
