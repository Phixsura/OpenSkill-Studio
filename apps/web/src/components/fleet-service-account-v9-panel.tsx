"use client";
export function FleetServiceAccountV9Panel({ total, overPrivileged }: { total: number; overPrivileged: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👤 Service Account v9</h3>
    <div className="text-sm">{total} accounts · {overPrivileged} over-privileged</div>
  </div>);
}
