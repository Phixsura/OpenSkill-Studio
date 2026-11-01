"use client";

interface Backup { backup_id: string; type: string; size_mb: number; status: string; created_at: string; }
interface BackupManagerPanelProps { backups: Backup[]; totalSizeMb: number;
  onCreateBackup: () => void; onRestore: (id: string) => void; onDelete: (id: string) => void; }

export function BackupManagerPanel({ backups, totalSizeMb, onCreateBackup, onRestore, onDelete }: BackupManagerPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Backups</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{totalSizeMb} MB total</span>
          <button onClick={onCreateBackup} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">New Backup</button>
        </div>
      </div>
      <div className="space-y-2">
        {backups.map(b => (
          <div key={b.backup_id} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{b.backup_id}</span>
                <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{b.type}</span>
              </div>
              <p className="text-xs text-gray-400">{new Date(b.created_at).toLocaleString()} · {b.size_mb} MB</p>
            </div>
            <div className="flex gap-2">
              <button onClick={() => onRestore(b.backup_id)} className="text-xs text-blue-500">Restore</button>
              <button onClick={() => onDelete(b.backup_id)} className="text-xs text-red-500">Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
