"use client";

interface MigrationInfo {
  migration_id: string;
  version: string;
  description: string;
  status: "pending" | "running" | "completed" | "failed" | "rolled_back";
  duration_ms: number | null;
  error: string;
}

interface MigrationTrackerCardProps {
  migrations: MigrationInfo[];
  appName: string;
}

const statusStyle: Record<string, string> = {
  pending: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  running: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  completed: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  rolled_back: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
};

export default function MigrationTrackerCard({ migrations, appName }: MigrationTrackerCardProps) {
  const completed = migrations.filter((m) => m.status === "completed").length;
  const failed = migrations.filter((m) => m.status === "failed").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🗃️ Migration Tracker
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right text-[11px] text-gray-400">
          <span>{completed} done</span>
          {failed > 0 && <span className="ml-1 text-red-500">· {failed} failed</span>}
        </div>
      </div>

      {migrations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No migrations</p>
      ) : (
        <div className="space-y-1.5">
          {migrations.map((m) => (
            <div
              key={m.migration_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[11px] text-gray-500">{m.version}</span>
                  <span className="text-xs text-gray-700 dark:text-gray-300">{m.description}</span>
                </div>
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusStyle[m.status] ?? ""}`}
                >
                  {m.status.replace("_", " ")}
                </span>
              </div>
              {m.duration_ms !== null && (
                <p className="mt-0.5 text-[10px] text-gray-400">{m.duration_ms}ms</p>
              )}
              {m.error && <p className="mt-0.5 text-[10px] text-red-500">{m.error}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
