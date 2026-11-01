"use client";
export function FleetResourceLockV9Panel({ locks, contentions }: { locks: number; contentions: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Resource Lock v9</h3>
    <div className="text-sm">{locks} locks · {contentions} contentions</div>
  </div>);
}
