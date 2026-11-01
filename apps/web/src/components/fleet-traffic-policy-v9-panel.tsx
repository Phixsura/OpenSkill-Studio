"use client";
export function FleetTrafficPolicyV9Panel({ policies, active }: { policies: number; active: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚦 Traffic Policy v9</h3>
    <div className="text-sm">{policies} policies · {active} active</div>
  </div>);
}
