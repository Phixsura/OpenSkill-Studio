"use client";

interface RollbackInfo {
  rollback_id: string;
  from_version: string;
  to_version: string;
  reason: string;
  status: "pending" | "in_progress" | "completed" | "failed" | "blocked";
  initiated_by: string;
  created_at: string;
}

interface RollbackManagerCardProps {
  rollbacks: RollbackInfo[];
  appName: string;
}

const STATUS_STYLES: Record<string, { icon: string; text: string }> = {
  pending: { icon: "⏳", text: "text-gray-500" },
  in_progress: { icon: "🔄", text: "text-blue-600 dark:text-blue-400" },
  completed: { icon: "✅", text: "text-green-600 dark:text-green-400" },
  failed: { icon: "❌", text: "text-red-600 dark:text-red-400" },
  blocked: { icon: "🚫", text: "text-yellow-600 dark:text-yellow-400" },
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function RollbackManagerCard({ rollbacks, appName }: RollbackManagerCardProps) {
  const activeCount = rollbacks.filter(
    (r) => r.status === "pending" || r.status === "in_progress",
  ).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Rollbacks</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {activeCount > 0 && (
          <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
            {activeCount} active
          </span>
        )}
      </div>

      {rollbacks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rollbacks</p>
      ) : (
        <div className="space-y-2">
          {rollbacks.map((r) => {
            const st = STATUS_STYLES[r.status] ?? STATUS_STYLES.pending;
            return (
              <div
                key={r.rollback_id}
                className="rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span>{st.icon}</span>
                    <span className="font-mono text-sm text-gray-800 dark:text-gray-200">
                      {r.from_version} → {r.to_version}
                    </span>
                  </div>
                  <span className={`text-xs font-medium capitalize ${st.text}`}>
                    {r.status.replace("_", " ")}
                  </span>
                </div>
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{r.reason}</p>
                <div className="mt-0.5 flex items-center gap-2 text-[11px] text-gray-400">
                  {r.initiated_by && <span>by {r.initiated_by}</span>}
                  <span>· {timeAgo(r.created_at)}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
