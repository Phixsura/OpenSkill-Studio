"use client";
export function FleetAiGovernanceV8Panel({ frameworks, active, policies, compliance, approvals }: { frameworks: number; active: number; policies: number; compliance: number; approvals: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ AI Governance v8</h3>
    <div className="text-sm">{active}/{frameworks} active · {policies} policies · {compliance}% · {approvals} approvals</div>
  </div>);
}
