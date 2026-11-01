"use client";
export function FleetChangeMgrV9Panel({ total, pending }: { total: number; pending: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Change Manager v9</h3>
    <div className="text-sm">{total} changes · {pending} pending</div>
  </div>);
}
