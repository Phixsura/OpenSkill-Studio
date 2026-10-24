"use client";
export function FleetAiWafV4Panel({ wafs, active, rules, blocked, mlRules }: { wafs: number; active: number; rules: number; blocked: number; mlRules: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI WAF v4</h3>
    <div className="text-sm">{active}/{wafs} active · {rules} rules · {blocked.toLocaleString()} blocked · {mlRules} ML rules</div>
  </div>);
}
