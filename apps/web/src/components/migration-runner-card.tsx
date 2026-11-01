"use client";

interface MigrationInfo {
  migration_id: string;
  version: number;
  description: string;
  status: "pending" | "running" | "applied" | "failed" | "rolled_back";
  applied_at: string | null;
  duration_ms: number | null;
  error: string | null;
}

interface MigrationRunnerCardProps {
  migrations: MigrationInfo[];
  appName: string;
  currentVersion: number;
}

const STATUS_STYLES: Record<string, { icon: string; text: string }> = {
  pending: { icon: "○", text: "text-gray-400" },
  running: { icon: "◎", text: "text-blue-600 dark:text-blue-400" },
  applied: { icon: "●", text: "text-green-600 dark:text-green-400" },
  failed: { icon: "✕", text: "text-red-600 dark:text-red-400" },
  rolled_back: { icon: "↩", text: "text-yellow-600 dark:text-yellow-400" },
};

export default function MigrationRunnerCard({
  migrations,
  appName,
  currentVersion,
}: MigrationRunnerCardProps) {
  const pendingCount = migrations.filter(
    (m) => m.status === "pending" || m.status === "failed",
  ).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Migrations</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-[10px] text-gray-600 dark:bg-gray-800 dark:text-gray-400">
            v{currentVersion}
          </span>
          {pendingCount > 0 && (
            <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
              {pendingCount} pending
            </span>
          )}
        </div>
      </div>

      {migrations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No migrations</p>
      ) : (
        <div className="space-y-1">
          {migrations.map((m) => {
            const st = STATUS_STYLES[m.status] ?? STATUS_STYLES.pending;
            return (
              <div
                key={m.migration_id}
                className="flex items-start gap-2.5 rounded px-2 py-2 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <span className={`mt-0.5 text-sm ${st.text}`}>{st.icon}</span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-[11px] text-gray-400">v{m.version}</span>
                    <span className="text-sm text-gray-800 dark:text-gray-200">
                      {m.description}
                    </span>
                  </div>
                  <div className="mt-0.5 flex items-center gap-2 text-[11px] text-gray-400">
                    <span className="capitalize">{m.status.replace("_", " ")}</span>
                    {m.duration_ms !== null && (
                      <>
                        <span>·</span>
                        <span>{m.duration_ms.toFixed(0)}ms</span>
                      </>
                    )}
                    {m.error && (
                      <>
                        <span>·</span>
                        <span className="text-red-500">{m.error}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
