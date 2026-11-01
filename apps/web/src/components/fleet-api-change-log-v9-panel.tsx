"use client";
export function FleetApiChangeLogV9Panel({ changes, breaking }: { changes: number; breaking: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 API Change Log v9</h3>
    <div className="text-sm">{changes} changes · {breaking} breaking</div>
  </div>);
}
