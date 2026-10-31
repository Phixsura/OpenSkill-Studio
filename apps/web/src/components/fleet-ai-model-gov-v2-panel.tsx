"use client";
export function FleetAiModelGovV2Panel({ frameworks, active, models, policies, compliance, approvals }: { frameworks: number; active: number; models: number; policies: number; compliance: number; approvals: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ AI Model Governance v2</h3>
    <div className="text-sm">{active}/{frameworks} active · {models} models · {policies} policies · {compliance}% · {approvals} approvals</div>
  </div>);
}
