"use client";
export function FleetEnv0Panel({ total, active, monthlyCost, ttlEnforced }: { total: number; active: number; monthlyCost: number; ttlEnforced: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 env0</h3>
    <div className="text-sm">{active}/{total} active · ${monthlyCost.toLocaleString()}/mo · {ttlEnforced} TTL enforced</div>
  </div>);
}
