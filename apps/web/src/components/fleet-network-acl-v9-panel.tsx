"use client";
export function FleetNetworkAclV9Panel({ acls, active }: { acls: number; active: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ Network ACL v9</h3>
    <div className="text-sm">{acls} ACLs · {active} active</div>
  </div>);
}
