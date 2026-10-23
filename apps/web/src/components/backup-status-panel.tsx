"use client";

interface Backup { id: string; status: string; sizeMb: number; createdAt: string; }
interface BackupStatusPanelProps { backups: Backup[]; totalSizeMb: number; successCount: number; total: number; }

export function BackupStatusPanel({ backups, totalSizeMb, successCount, total }: BackupStatusPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Backups</h3>
        <span className="text-xs text-gray-400">{successCount}/{total} · {totalSizeMb}MB</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {backups.map(b => (
          <div key={b.id} className="flex items-center justify-between px-4 py-2">
            <div className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${b.status === "completed" ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-sm font-mono">{b.id}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              <span>{b.sizeMb}MB</span>
              <span>{b.createdAt}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
