"use client";

interface RetryOperation {
  operation_id: string;
  attempt: number;
  max_retries: number;
  strategy: "fixed" | "linear" | "exponential" | "exponential_jitter";
  next_delay_seconds: number | null;
  exhausted: boolean;
  first_attempt_at: string;
  last_attempt_at: string | null;
}

interface RetryPolicyCardProps {
  operations: RetryOperation[];
  appName: string;
}

const STRATEGY_LABELS: Record<string, string> = {
  fixed: "Fixed",
  linear: "Linear",
  exponential: "Exponential",
  exponential_jitter: "Exp + Jitter",
};

function AttemptBar({ attempt, max }: { attempt: number; max: number }) {
  const pct = max > 0 ? Math.min((attempt / max) * 100, 100) : 0;
  const color = pct >= 80 ? "bg-red-500" : pct >= 50 ? "bg-yellow-500" : "bg-blue-500";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[11px] text-gray-500">
        {attempt}/{max}
      </span>
    </div>
  );
}

function timeAgo(iso: string | null): string {
  if (!iso) return "—";
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function RetryPolicyCard({ operations, appName }: RetryPolicyCardProps) {
  const exhaustedCount = operations.filter((o) => o.exhausted).length;
  const retryingCount = operations.filter((o) => !o.exhausted && o.attempt > 0).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Retry Policy</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-2">
          {retryingCount > 0 && (
            <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
              {retryingCount} retrying
            </span>
          )}
          {exhaustedCount > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {exhaustedCount} exhausted
            </span>
          )}
        </div>
      </div>

      {operations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No retry operations</p>
      ) : (
        <div className="space-y-2.5">
          {operations.map((op) => (
            <div
              key={op.operation_id}
              className={`rounded-lg border px-3 py-2.5 ${
                op.exhausted
                  ? "border-red-200 bg-red-50/50 dark:border-red-900/50 dark:bg-red-950/20"
                  : "border-gray-100 dark:border-gray-800"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm text-gray-800 dark:text-gray-200">
                    {op.operation_id}
                  </span>
                  <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                    {STRATEGY_LABELS[op.strategy] ?? op.strategy}
                  </span>
                </div>
                {op.exhausted && (
                  <span className="text-xs font-medium text-red-600 dark:text-red-400">
                    Exhausted
                  </span>
                )}
              </div>
              <div className="mt-1.5 flex items-center justify-between">
                <AttemptBar attempt={op.attempt} max={op.max_retries} />
                <div className="text-[11px] text-gray-400">
                  {op.next_delay_seconds !== null && !op.exhausted
                    ? `Next in ${op.next_delay_seconds.toFixed(1)}s`
                    : ""}
                </div>
              </div>
              <div className="mt-1 text-[11px] text-gray-400">
                Started {timeAgo(op.first_attempt_at)}
                {op.last_attempt_at && ` · Last attempt ${timeAgo(op.last_attempt_at)}`}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
