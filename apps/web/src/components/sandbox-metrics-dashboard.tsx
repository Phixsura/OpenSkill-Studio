"use client";

interface SandboxMetrics {
  extensionId: string;
  executions: number;
  avgCpuMs: number;
  avgMemoryMb: number;
  peakMemoryMb: number;
  memoryLimitMb: number;
  totalIoOps: number;
  successRate: number;
  avgDurationMs: number;
  quotaUsedPercent: number;
}

export function SandboxMetricsDashboard({
  metrics,
  onViewLogs,
}: {
  metrics: SandboxMetrics;
  onViewLogs?: () => void;
}) {
  const memPercent = Math.round((metrics.peakMemoryMb / metrics.memoryLimitMb) * 100);
  const successColor = metrics.successRate >= 99 ? "text-green-500" : metrics.successRate >= 90 ? "text-yellow-500" : "text-red-500";

  return (
    <div className="rounded-xl border dark:border-gray-700 p-5 space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📊 Sandbox Metrics</h2>
        {onViewLogs && (
          <button onClick={onViewLogs} className="text-xs text-blue-500 border border-blue-300 dark:border-blue-700 px-3 py-1 rounded">
            📋 View Logs
          </button>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricTile label="Executions" value={metrics.executions.toLocaleString()} icon="🔄" />
        <MetricTile label="Success Rate" value={`${metrics.successRate}%`} icon="✅"
          valueColor={successColor} />
        <MetricTile label="Avg Duration" value={`${metrics.avgDurationMs}ms`} icon="⏱️" />
        <MetricTile label="Total I/O" value={metrics.totalIoOps.toLocaleString()} icon="💾" />
      </div>

      {/* CPU gauge */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">CPU Usage (avg)</span>
          <span className="font-mono">{metrics.avgCpuMs}ms per execution</span>
        </div>
      </div>

      {/* Memory gauge */}
      <div className="space-y-1">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Memory</span>
          <span className="font-mono">{metrics.peakMemoryMb}/{metrics.memoryLimitMb}MB peak ({memPercent}%)</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div className={`h-2 rounded-full ${memPercent > 90 ? "bg-red-500" : memPercent > 70 ? "bg-yellow-500" : "bg-green-500"}`}
            style={{ width: `${Math.min(100, memPercent)}%` }} />
        </div>
        <div className="text-xs text-gray-400">Avg: {metrics.avgMemoryMb}MB</div>
      </div>

      {/* Quota */}
      <div className="space-y-1">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Quota Used</span>
          <span className={`font-mono ${metrics.quotaUsedPercent > 90 ? "text-red-500 font-bold" : ""}`}>
            {metrics.quotaUsedPercent}%
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div className={`h-2 rounded-full ${metrics.quotaUsedPercent > 90 ? "bg-red-500" : "bg-blue-500"}`}
            style={{ width: `${Math.min(100, metrics.quotaUsedPercent)}%` }} />
        </div>
      </div>
    </div>
  );
}

function MetricTile({ label, value, icon, valueColor }: {
  label: string; value: string; icon: string; valueColor?: string;
}) {
  return (
    <div className="rounded-lg bg-gray-50 dark:bg-gray-800 p-3 text-center">
      <div className="text-lg">{icon}</div>
      <div className={`text-xl font-bold ${valueColor || ""}`}>{value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}
