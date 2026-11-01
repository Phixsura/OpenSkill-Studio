"use client";

interface RetentionPolicyInfo {
  policy_id: string;
  log_type: string;
  retention_days: number;
  max_size_mb: number;
  current_size_mb: number;
  entry_count: number;
  needs_cleanup: boolean;
}

interface LogRetentionCardProps {
  policies: RetentionPolicyInfo[];
  totalSizeMb: number;
  appName: string;
}

function formatSize(mb: number): string {
  if (mb >= 1024) return `${(mb / 1024).toFixed(1)} GB`;
  return `${mb.toFixed(0)} MB`;
}

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function LogRetentionCard({
  policies,
  totalSizeMb,
  appName,
}: LogRetentionCardProps) {
  const cleanupNeeded = policies.filter((p) => p.needs_cleanup).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Log Retention</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{formatSize(totalSizeMb)} total</span>
          {cleanupNeeded > 0 && (
            <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
              {cleanupNeeded} need cleanup
            </span>
          )}
        </div>
      </div>

      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No retention policies</p>
      ) : (
        <div className="space-y-2">
          {policies.map((p) => {
            const usagePct =
              p.max_size_mb > 0 ? Math.min((p.current_size_mb / p.max_size_mb) * 100, 100) : 0;
            const barColor = p.needs_cleanup
              ? "bg-red-500"
              : usagePct >= 80
                ? "bg-yellow-500"
                : "bg-blue-500";
            return (
              <div
                key={p.policy_id}
                className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-800 dark:text-gray-200">{p.log_type}</span>
                    <span className="text-[10px] text-gray-400">{p.retention_days}d retention</span>
                  </div>
                  <span className="text-[11px] text-gray-500">
                    {formatNum(p.entry_count)} entries
                  </span>
                </div>
                {p.max_size_mb > 0 && (
                  <div className="mt-1 flex items-center gap-2">
                    <div className="h-1.5 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
                      <div
                        className={`h-1.5 rounded-full ${barColor}`}
                        style={{ width: `${usagePct}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-gray-400">
                      {formatSize(p.current_size_mb)}/{formatSize(p.max_size_mb)}
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
