"use client";
export function FleetAiNetPolicyPanel({ policies, active, rules, blocked, allowed }: { policies: number; active: number; rules: number; blocked: number; allowed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 AI Network Policy</h3>
    <div className="text-sm">{active}/{policies} active · {rules} rules · {blocked.toLocaleString()} blocked · {allowed.toLocaleString()} allowed</div>
  </div>);
}
