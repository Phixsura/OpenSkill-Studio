"use client";
export function FleetDistributedLockV9Panel({ locks, contended }: { locks: number; contended: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Distributed Lock v9</h3>
    <div className="text-sm">{locks} locks · {contended} contended</div>
  </div>);
}
