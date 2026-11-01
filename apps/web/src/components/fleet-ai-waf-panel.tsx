"use client";
export function FleetAiWafPanel({ wafs, active, requests, blocked, rules }: { wafs: number; active: number; requests: number; blocked: number; rules: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI WAF</h3>
    <div className="text-sm">{active}/{wafs} active · {requests.toLocaleString()} req · {blocked.toLocaleString()} blocked · {rules} rules</div>
  </div>);
}
