"use client";

interface BackupSummary { totalBackups: number; byDatabase: Record<string, number>;
  totalSizeMb: number; verifiedCount: number; unverifiedCount: number; }
interface BackupStatusPanelProps { summary: BackupSummary; onBackupNow: () => void; }

export function BackupStatusPanel({ summary, onBackupNow }: BackupStatusPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">💾 Database Backups</h3>
        <button onClick={onBackupNow}
          className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">Backup Now</button>
      </div>
      <div className="grid grid-cols-4 gap-3 text-center mb-4">
        <div><p className="text-lg font-bold">{summary.totalBackups}</p><p className="text-xs text-gray-400">Total</p></div>
        <div><p className="text-lg font-bold">{(summary.totalSizeMb / 1024).toFixed(1)} GB</p><p className="text-xs text-gray-400">Size</p></div>
        <div><p className="text-lg font-bold text-green-600">{summary.verifiedCount}</p><p className="text-xs text-gray-400">Verified</p></div>
        <div><p className="text-lg font-bold text-yellow-600">{summary.unverifiedCount}</p><p className="text-xs text-gray-400">Unverified</p></div>
      </div>
      <div>
        <h4 className="text-xs font-semibold text-gray-400 mb-2">By Database</h4>
        {Object.entries(summary.byDatabase).map(([db, count]) => (
          <div key={db} className="flex justify-between text-sm py-1">
            <span>{db}</span><span className="text-gray-400">{count} backups</span>
          </div>
        ))}
      </div>
    </div>
  );
}
