"use client";
export function FleetK8sRbacV9Panel({ roles, overPrivileged }: { roles: number; overPrivileged: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ K8s RBAC v9</h3>
    <div className="text-sm">{roles} roles · {overPrivileged} over-privileged</div>
  </div>);
}
