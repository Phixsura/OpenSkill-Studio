"use client";
export function FleetCloudMigrationV9Panel({ total, migrated }: { total: number; migrated: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ Cloud Migration v9</h3>
    <div className="text-sm">{total} workloads · {migrated} migrated</div>
  </div>);
}
