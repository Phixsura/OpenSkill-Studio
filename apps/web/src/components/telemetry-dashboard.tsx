"use client";

interface TelemetrySummary {
  installation_id: string;
  total_metrics: number;
  total_errors: number;
  total_spans: number;
  error_rate: number;
  avg_span_ms: number;
  top_errors: [string, number][];
  top_slow_ops: [string, number][];
}

interface TelemetryDashboardProps {
  summary: TelemetrySummary;
  appName: string;
  quotaUsed: number;
  quotaLimit: number;
}

function StatTile({
  label,
  value,
  sub,
  warn,
}: {
  label: string;
  value: string;
  sub?: string;
  warn?: boolean;
}) {
  return (
    <div className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
      <p className={`text-lg font-bold ${warn ? "text-red-600" : ""}`}>{value}</p>
      <p className="text-[10px] text-gray-500">{label}</p>
      {sub && <p className="text-[10px] text-gray-400">{sub}</p>}
    </div>
  );
}

function RankList({
  title,
  items,
  unit,
}: {
  title: string;
  items: [string, number][];
  unit: string;
}) {
  if (items.length === 0) return null;
  return (
    <div>
      <p className="text-[10px] font-semibold uppercase text-gray-400">{title}</p>
      <ul className="mt-1 space-y-1">
        {items.map(([name, value], i) => (
          <li key={name} className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-1.5">
              <span className="text-gray-400">{i + 1}.</span>
              <code className="font-medium">{name}</code>
            </span>
            <span className="text-gray-500">
              {typeof value === "number" && value % 1 !== 0 ? value.toFixed(1) : value}
              {unit}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function TelemetryDashboard({
  summary,
  appName,
  quotaUsed,
  quotaLimit,
}: TelemetryDashboardProps) {
  const quotaPct = quotaLimit > 0 ? Math.round((quotaUsed / quotaLimit) * 100) : 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Telemetry</h2>
          <p className="text-xs text-gray-500">{appName}</p>
        </div>
        <div className="text-right text-xs">
          <p className="text-gray-500">
            Quota: {quotaUsed.toLocaleString()}/{quotaLimit.toLocaleString()}
          </p>
          <div className="mt-0.5 h-1.5 w-24 rounded-full bg-gray-200 dark:bg-gray-700">
            <div
              className={`h-full rounded-full ${quotaPct >= 90 ? "bg-red-500" : "bg-blue-500"}`}
              style={{ width: `${Math.min(quotaPct, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-5 gap-2">
        <StatTile label="Metrics" value={summary.total_metrics.toLocaleString()} />
        <StatTile
          label="Errors"
          value={summary.total_errors.toLocaleString()}
          warn={summary.total_errors > 0}
        />
        <StatTile label="Spans" value={summary.total_spans.toLocaleString()} />
        <StatTile
          label="Error Rate"
          value={`${summary.error_rate}%`}
          warn={summary.error_rate > 5}
        />
        <StatTile
          label="Avg Span"
          value={`${summary.avg_span_ms}ms`}
          sub={summary.avg_span_ms > 500 ? "slow" : "ok"}
        />
      </div>

      {/* Rankings */}
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-lg border border-gray-200 p-3 dark:border-gray-700">
          {summary.top_errors.length > 0 ? (
            <RankList title="Top Errors" items={summary.top_errors} unit="×" />
          ) : (
            <div className="py-3 text-center">
              <span className="text-xl">✅</span>
              <p className="mt-1 text-[10px] text-gray-500">No errors</p>
            </div>
          )}
        </div>
        <div className="rounded-lg border border-gray-200 p-3 dark:border-gray-700">
          {summary.top_slow_ops.length > 0 ? (
            <RankList title="Slowest Operations" items={summary.top_slow_ops} unit="ms" />
          ) : (
            <div className="py-3 text-center">
              <span className="text-xl">⚡</span>
              <p className="mt-1 text-[10px] text-gray-500">No spans</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
