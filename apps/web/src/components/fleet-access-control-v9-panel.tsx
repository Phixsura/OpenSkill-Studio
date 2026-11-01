"use client";
export function FleetAccessControlV9Panel({ policies, roles }: { policies: number; roles: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 Access Control v9</h3>
    <div className="text-sm">{policies} policies · {roles} roles</div>
  </div>);
}
