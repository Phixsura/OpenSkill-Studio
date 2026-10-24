"use client";
export function FleetAiGovV5Panel({ frameworks, active, policies, approvals, compliance }: { frameworks: number; active: number; policies: number; approvals: number; compliance: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ AI Governance v5</h3>
    <div className="text-sm">{active}/{frameworks} active · {policies} policies · {approvals} approvals · {compliance}%</div>
  </div>);
}
