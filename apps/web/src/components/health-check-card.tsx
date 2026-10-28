"use client";

interface ProbeInfo {
  probe_id: string;
  endpoint: string;
  healthy: boolean;
  consecutive_failures: int;
  total_checks: number;
  availability_pct: number;
  last_check_result: "pass" | "fail" | "timeout" | null;
  last_check_latency_ms: number | null;
  last_failure_message: string | null;
}

interface HealthCheckCardProps {
  probes: ProbeInfo[];
  appName: string;
}

function AvailabilityDot({ pct }: { pct: number }) {
  const color = pct >= 99.9 ? "bg-green-500" : pct >= 99 ? "bg-yellow-500" : "bg-red-500";
  return <span className={`inline-block h-2.5 w-2.5 rounded-full ${color}`} />;
}

function LatencyLabel({ ms }: { ms: number | null }) {
  if (ms === null) return <span className="text-gray-400">—</span>;
  const color =
    ms < 200
      ? "text-green-600 dark:text-green-400"
      : ms < 1000
        ? "text-yellow-600 dark:text-yellow-400"
        : "text-red-600 dark:text-red-400";
  return <span className={`font-mono text-xs ${color}`}>{ms.toFixed(0)}ms</span>;
}

function ResultBadge({ result }: { result: string | null }) {
  if (!result) return null;
  const styles: Record<string, { bg: string; text: string; label: string }> = {
    pass: {
      bg: "bg-green-100 dark:bg-green-900/30",
      text: "text-green-700 dark:text-green-400",
      label: "Pass",
    },
    fail: {
      bg: "bg-red-100 dark:bg-red-900/30",
      text: "text-red-700 dark:text-red-400",
      label: "Fail",
    },
    timeout: {
      bg: "bg-yellow-100 dark:bg-yellow-900/30",
      text: "text-yellow-700 dark:text-yellow-400",
      label: "Timeout",
    },
  };
  const st = styles[result] ?? styles.fail;
  return (
    <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${st.bg} ${st.text}`}>
      {st.label}
    </span>
  );
}

export default function HealthCheckCard({ probes, appName }: HealthCheckCardProps) {
  const unhealthyCount = probes.filter((p) => !p.healthy).length;
  const overallAvail =
    probes.length > 0
      ? probes.reduce((sum, p) => sum + p.availability_pct, 0) / probes.length
      : 100;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Health Checks</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="font-mono text-lg font-bold text-gray-800 dark:text-gray-200">
            {overallAvail.toFixed(1)}%
          </span>
          {unhealthyCount > 0 ? (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {unhealthyCount} unhealthy
            </span>
          ) : (
            <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
              All healthy
            </span>
          )}
        </div>
      </div>

      {/* Probe list */}
      {probes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No probes configured</p>
      ) : (
        <div className="space-y-3">
          {probes.map((p) => (
            <div
              key={p.probe_id}
              className={`rounded-lg border p-3 ${
                p.healthy
                  ? "border-gray-100 dark:border-gray-800"
                  : "border-red-200 bg-red-50/50 dark:border-red-900/50 dark:bg-red-950/20"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AvailabilityDot pct={p.availability_pct} />
                  <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                    {p.endpoint}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <LatencyLabel ms={p.last_check_latency_ms} />
                  <ResultBadge result={p.last_check_result} />
                </div>
              </div>
              <div className="mt-1.5 flex items-center justify-between">
                <span className="text-[11px] text-gray-400">
                  {p.availability_pct.toFixed(1)}% uptime · {p.total_checks} checks
                </span>
                {!p.healthy && (
                  <span className="text-[11px] text-red-500">
                    {p.consecutive_failures} consecutive failures
                    {p.last_failure_message ? ` · ${p.last_failure_message}` : ""}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
