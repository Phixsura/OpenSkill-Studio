"use client";
export function FleetWafPanel({ rules, blocked, allowed, blockRate }: { rules: number; blocked: number; allowed: number; blockRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ WAF</h3>
    <div className="text-sm">{blocked.toLocaleString()} blocked · {allowed.toLocaleString()} allowed ({blockRate}%)</div>
    <div className="text-xs text-gray-400">{rules} rules active</div>
  </div>);
}
