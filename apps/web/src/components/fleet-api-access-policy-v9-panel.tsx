"use client";
export function FleetApiAccessPolicyV9Panel({ policies, enforced }: { policies: number; enforced: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 API Access Policy v9</h3>
    <div className="text-sm">{policies} policies · {enforced} enforced</div>
  </div>);
}
