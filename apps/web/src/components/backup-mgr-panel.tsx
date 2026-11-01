"use client";

interface BackupInfo { name: string; sizeMb: number; type: string; status: string; }
interface BackupMgrPanelProps { backups: BackupInfo[]; totalSizeMb: number;
  retentionDays: number; }

export function BackupMgrPanel({ backups, totalSizeMb, retentionDays }: BackupMgrPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💾 Backups</h3>
        <span className="text-xs text-gray-400">{backups.length} backups · {totalSizeMb}MB · {retentionDays}d retention</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {backups.map(b => (
          <div key={b.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-mono">{b.name}</span>
              <span className="px-1 rounded bg-gray-100 dark:bg-gray-800 text-[10px]">{b.type}</span>
            </div>
            <span className="text-gray-400">{b.sizeMb}MB</span>
          </div>
        ))}
      </div>
    </div>
  );
}
