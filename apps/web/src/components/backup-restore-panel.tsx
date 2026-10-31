"use client";

interface Backup { backup_id: string; created_at: string; size_bytes: number; webhooks_count: number; secrets_count: number; }
interface BackupRestorePanelProps { backups: Backup[]; onBackup: () => void; onRestore: (backupId: string) => void; }

export function BackupRestorePanel({ backups, onBackup, onRestore }: BackupRestorePanelProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Backups</h3>
        <button onClick={onBackup} className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white hover:bg-blue-700">
          Create Backup
        </button>
      </div>
      {backups.length === 0 ? (
        <p className="mt-3 text-sm text-gray-400">No backups yet.</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {backups.map(b => (
            <li key={b.backup_id} className="flex items-center justify-between rounded border p-2 text-sm dark:border-gray-700">
              <div>
                <p className="font-mono text-xs">{b.backup_id}</p>
                <p className="text-xs text-gray-400">{new Date(b.created_at).toLocaleString()} · {Math.round(b.size_bytes / 1024)}KB</p>
              </div>
              <button onClick={() => onRestore(b.backup_id)} className="rounded border px-2 py-1 text-xs hover:bg-gray-50 dark:border-gray-600">
                Restore
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
