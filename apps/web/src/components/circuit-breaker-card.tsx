"use client";

interface BreakerInfo {
  service: string;
  state: "closed" | "open" | "half_open";
  failure_count: number;
  failure_threshold: number;
  success_count: number;
  success_threshold: number;
  last_failure_at: string | null;
  opened_at: string | null;
  recovery_timeout_seconds: number;
}

interface CircuitBreakerCardProps {
  breakers: BreakerInfo[];
  appName: string;
}

const STATE_STYLES: Record<string, { label: string; bg: string; text: string; dot: string }> = {
  closed: {
    label: "Closed",
    bg: "bg-green-100 dark:bg-green-900/30",
    text: "text-green-700 dark:text-green-400",
    dot: "bg-green-500",
  },
  open: {
    label: "Open",
    bg: "bg-red-100 dark:bg-red-900/30",
    text: "text-red-700 dark:text-red-400",
    dot: "bg-red-500",
  },
  half_open: {
    label: "Half-Open",
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
    dot: "bg-yellow-500",
  },
};

function StateBadge({ state }: { state: string }) {
  const st = STATE_STYLES[state] ?? STATE_STYLES.closed;
  return (
    <span
      data-testid={`state-${state}`}
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${st.bg} ${st.text}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${st.dot}`} />
      {st.label}
    </span>
  );
}

function FailureBar({ count, threshold }: { count: number; threshold: number }) {
  const pct = Math.min((count / threshold) * 100, 100);
  const color = pct >= 80 ? "bg-red-500" : pct >= 50 ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          className={`h-1.5 rounded-full ${color}`}
          style={{ width: `${pct}%` }}
          data-testid="failure-bar"
        />
      </div>
      <span className="text-xs text-gray-500 dark:text-gray-400">
        {count}/{threshold}
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

export default function CircuitBreakerCard({ breakers, appName }: CircuitBreakerCardProps) {
  const openCount = breakers.filter((b) => b.state === "open").length;
  const halfOpenCount = breakers.filter((b) => b.state === "half_open").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Circuit Breakers
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-2">
          {openCount > 0 && (
            <span
              data-testid="open-count"
              className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400"
            >
              {openCount} open
            </span>
          )}
          {halfOpenCount > 0 && (
            <span
              data-testid="half-open-count"
              className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
            >
              {halfOpenCount} probing
            </span>
          )}
          {openCount === 0 && halfOpenCount === 0 && (
            <span
              data-testid="all-healthy"
              className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400"
            >
              All healthy
            </span>
          )}
        </div>
      </div>

      {/* Breaker list */}
      {breakers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No circuit breakers configured</p>
      ) : (
        <ul className="divide-y divide-gray-100 dark:divide-gray-800" data-testid="breaker-list">
          {breakers.map((b) => (
            <li
              key={b.service}
              className="flex items-center justify-between py-3 first:pt-0 last:pb-0"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="truncate text-sm font-medium text-gray-800 dark:text-gray-200">
                    {b.service}
                  </span>
                  <StateBadge state={b.state} />
                </div>
                <div className="mt-1.5">
                  <FailureBar count={b.failure_count} threshold={b.failure_threshold} />
                </div>
                {b.state === "open" && b.opened_at && (
                  <p className="mt-1 text-[11px] text-gray-400">
                    Opened {timeAgo(b.opened_at)} · recovery in {b.recovery_timeout_seconds}s
                  </p>
                )}
                {b.state === "half_open" && (
                  <p className="mt-1 text-[11px] text-gray-400">
                    Probing: {b.success_count}/{b.success_threshold} successes
                  </p>
                )}
                {b.state === "closed" && b.last_failure_at && (
                  <p className="mt-1 text-[11px] text-gray-400">
                    Last failure {timeAgo(b.last_failure_at)}
                  </p>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
