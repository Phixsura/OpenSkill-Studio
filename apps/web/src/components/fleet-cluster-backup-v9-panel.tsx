"use client";
export function FleetClusterBackupV9Panel({ backups, ageHours }: { backups: number; ageHours: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 Cluster Backup v9</h3>
    <div className="text-sm">{backups} backups · {ageHours}h newest</div>
  </div>);
}
