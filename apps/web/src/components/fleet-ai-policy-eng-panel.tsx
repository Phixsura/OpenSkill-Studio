"use client";
export function FleetAiPolicyEngPanel({ engines, active, policies, evals, violations }: { engines: number; active: number; policies: number; evals: number; violations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Policy Engine</h3>
    <div className="text-sm">{active}/{engines} active · {policies} policies · {evals.toLocaleString()} evals · {violations} violations</div>
  </div>);
}
