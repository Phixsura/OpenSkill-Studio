"use client";
export function FleetSnapshotMgrV9Panel({ total, sizeGb }: { total: number; sizeGb: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📸 Snapshot Manager v9</h3>
    <div className="text-sm">{total} snapshots · {sizeGb} GB</div>
  </div>);
}
