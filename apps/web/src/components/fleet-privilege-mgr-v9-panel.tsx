"use client";
export function FleetPrivilegeMgrV9Panel({ total, approved }: { total: number; approved: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👑 Privilege Manager v9</h3>
    <div className="text-sm">{total} requests · {approved} approved</div>
  </div>);
}
