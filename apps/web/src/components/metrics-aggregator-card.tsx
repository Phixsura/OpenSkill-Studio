"use client";

interface MetricSummary {
  metric: string;
  sum: number;
  avg: number;
  min: number;
  max: number;
  count: number;
  p99: number;
}

interface MetricsAggregatorCardProps {
  metrics: MetricSummary[];
  appName: string;
}

function formatValue(v: number): string {
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(1)}K`;
  if (v % 1 !== 0) return v.toFixed(2);
  return v.toString();
}

function StatCell({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <p className="font-mono text-sm font-medium text-gray-800 dark:text-gray-200">{value}</p>
      <p className="text-[9px] uppercase tracking-wider text-gray-400">{label}</p>
    </div>
  );
}

export default function MetricsAggregatorCard({ metrics, appName }: MetricsAggregatorCardProps) {
  const totalPoints = metrics.reduce((s, m) => s + m.count, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Metrics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {metrics.length} metric{metrics.length !== 1 ? "s" : ""} · {formatValue(totalPoints)}{" "}
          points
        </span>
      </div>

      {metrics.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No metrics collected</p>
      ) : (
        <div className="space-y-3">
          {metrics.map((m) => (
            <div
              key={m.metric}
              className="rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800"
            >
              <div className="mb-2 flex items-center justify-between">
                <span className="font-mono text-sm font-medium text-gray-800 dark:text-gray-200">
                  {m.metric}
                </span>
                <span className="text-[11px] text-gray-400">{formatValue(m.count)} pts</span>
              </div>
              <div className="grid grid-cols-5 gap-2">
                <StatCell label="avg" value={formatValue(m.avg)} />
                <StatCell label="min" value={formatValue(m.min)} />
                <StatCell label="max" value={formatValue(m.max)} />
                <StatCell label="sum" value={formatValue(m.sum)} />
                <StatCell label="p99" value={formatValue(m.p99)} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
