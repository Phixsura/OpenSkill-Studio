"use client";

interface RetryScheduleInfo {
  attempt: number;
  delay_seconds: number;
  should_retry: boolean;
}

interface WebhookRetryPolicyCardProps {
  policyId: string;
  strategy: "fixed" | "linear" | "exponential";
  maxRetries: number;
  schedule: RetryScheduleInfo[];
  appName: string;
}

const STRATEGY_LABELS: Record<string, string> = {
  fixed: "Fixed",
  linear: "Linear",
  exponential: "Exponential",
};

function formatDelay(s: number): string {
  if (s >= 3600) return `${(s / 3600).toFixed(1)}h`;
  if (s >= 60) return `${(s / 60).toFixed(0)}m`;
  return `${s}s`;
}

export default function WebhookRetryPolicyCard({
  policyId,
  strategy,
  maxRetries,
  schedule,
  appName,
}: WebhookRetryPolicyCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Retry Policy</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {appName} · {policyId}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
            {STRATEGY_LABELS[strategy] ?? strategy}
          </span>
          <span className="text-xs text-gray-400">{maxRetries} max</span>
        </div>
      </div>

      <div className="space-y-1">
        {schedule.map((s) => (
          <div
            key={s.attempt}
            className={`flex items-center justify-between rounded px-2 py-1 text-xs ${
              s.should_retry ? "text-gray-700 dark:text-gray-300" : "text-gray-400 line-through"
            }`}
          >
            <span>Attempt {s.attempt + 1}</span>
            <span className="font-mono">{s.should_retry ? formatDelay(s.delay_seconds) : "—"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
