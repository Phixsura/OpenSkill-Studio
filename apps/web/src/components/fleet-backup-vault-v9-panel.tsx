"use client";
export function FleetBackupVaultV9Panel({ total, sizeGb }: { total: number; sizeGb: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 Backup Vault v9</h3>
    <div className="text-sm">{total} backups · {sizeGb} GB stored</div>
  </div>);
}
