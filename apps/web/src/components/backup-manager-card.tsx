"use client";

interface BackupInfo {
  backup_id: string;
  status: "pending" | "in_progress" | "completed" | "failed" | "restored";
  size_mb: number;
  label: string;
  created_at: string;
}

interface BackupManagerCardProps {
  backups: BackupInfo[];
  totalSizeMb: number;
  appName: string;
}

const STATUS_ICONS: Record<string, string> = {
  pending: "⏳",
  in_progress: "⚙️",
  completed: "✅",
  failed: "❌",
  restored: "🔄",
};

function formatSize(mb: number): string {
  if (mb >= 1024) return `${(mb / 1024).toFixed(1)} GB`;
  return `${mb.toFixed(0)} MB`;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function BackupManagerCard({
  backups,
  totalSizeMb,
  appName,
}: BackupManagerCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Backups</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {backups.length} backups · {formatSize(totalSizeMb)}
        </span>
      </div>

      {backups.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No backups</p>
      ) : (
        <div className="space-y-1.5">
          {backups.map((b) => (
            <div
              key={b.backup_id}
              className="flex items-center justify-between rounded px-2.5 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span>{STATUS_ICONS[b.status] ?? "📦"}</span>
                <div>
                  <span className="text-xs text-gray-800 dark:text-gray-200">
                    {b.label || b.backup_id}
                  </span>
                  <p className="text-[10px] text-gray-400">{timeAgo(b.created_at)}</p>
                </div>
              </div>
              <span className="text-[11px] text-gray-400">{formatSize(b.size_mb)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
