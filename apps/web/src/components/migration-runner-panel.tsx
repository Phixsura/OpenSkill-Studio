"use client";

interface Migration {
  migrationId: string;
  version: string;
  name: string;
  state: "pending" | "applied" | "failed" | "rolled_back";
  error?: string;
}

interface MigrationStatus {
  total: number;
  applied: number;
  pending: number;
  failed: number;
  currentVersion: string | null;
}

const stateConfig: Record<string, { color: string; icon: string }> = {
  pending: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", icon: "⏳" },
  applied: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "✅" },
  failed: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "❌" },
  rolled_back: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "↩" },
};

export function MigrationRunnerPanel({
  migrations,
  status,
  onMigrateUp,
  onRollbackLast,
}: {
  migrations: Migration[];
  status: MigrationStatus;
  onMigrateUp?: () => void;
  onRollbackLast?: () => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔄 Migrations</h2>
        <div className="flex items-center gap-2">
          {status.currentVersion && (
            <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 px-2 py-0.5 rounded-full">
              v{status.currentVersion}
            </span>
          )}
          <button onClick={onMigrateUp} disabled={status.pending === 0}
            className="text-xs bg-green-600 text-white px-2 py-1 rounded disabled:opacity-50">Migrate Up</button>
          <button onClick={onRollbackLast} disabled={status.applied === 0}
            className="text-xs bg-yellow-600 text-white px-2 py-1 rounded disabled:opacity-50">Rollback</button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Total</span>
          <span className="font-bold">{status.total}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Applied</span>
          <span className="font-bold text-green-600">{status.applied}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Pending</span>
          <span className="font-bold text-yellow-600">{status.pending}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Failed</span>
          <span className="font-bold text-red-600">{status.failed}</span>
        </div>
      </div>

      <div className="space-y-0.5">
        {migrations.map((m) => {
          const cfg = stateConfig[m.state];
          return (
            <div key={m.migrationId} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span>{cfg.icon}</span>
                <code className="text-xs font-bold">{m.version}</code>
                <span className="text-sm">{m.name}</span>
              </div>
              <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{m.state}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
