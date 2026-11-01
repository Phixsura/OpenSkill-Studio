"use client";
export function FleetMeshPolicyV9Panel({ total, enforced }: { total: number; enforced: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ Mesh Policy v9</h3>
    <div className="text-sm">{total} policies · {enforced} enforced</div>
  </div>);
}
