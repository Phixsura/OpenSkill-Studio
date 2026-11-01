"use client";

interface ResourceSnapshot {
  timestamp: string;
  cpuPercent: number;
  memoryMb: number;
  diskMb: number;
  networkBytes: number;
  activeConnections: number;
}

interface ResourceAlert {
  id: string;
  resource: string;
  level: "warning" | "critical" | "throttled";
  value: number;
  message: string;
  timestamp: string;
}

interface ResourceLimits {
  cpuCores: number;
  memoryMb: number;
  diskMb: number;
}

function ProgressBar({ value, max, color }: { value: number; max: number; color: string }) {
  const pct = Math.min((value / max) * 100, 100);
  const bg = pct > 90 ? "bg-red-500" : pct > 70 ? "bg-yellow-500" : color;
  return (
    <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
      <div className={`h-full ${bg} rounded-full transition-all`} style={{ width: `${pct}%` }} />
    </div>
  );
}

const alertColors: Record<string, string> = {
  warning: "border-yellow-400 bg-yellow-50 dark:bg-yellow-900/20",
  critical: "border-red-400 bg-red-50 dark:bg-red-900/20",
  throttled: "border-purple-400 bg-purple-50 dark:bg-purple-900/20",
};

export function ResourceMonitorDashboard({
  sandboxId,
  current,
  limits,
  alerts,
  isThrottled,
}: {
  sandboxId: string;
  current: ResourceSnapshot | null;
  limits: ResourceLimits;
  alerts: ResourceAlert[];
  isThrottled: boolean;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📈 Resource Monitor</h2>
        {isThrottled && (
          <span className="text-xs bg-red-600 text-white px-2 py-1 rounded-full animate-pulse">
            ⚠ THROTTLED
          </span>
        )}
      </div>

      {current ? (
        <div className="grid gap-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>CPU</span>
              <span className="font-mono">{current.cpuPercent.toFixed(1)}%</span>
            </div>
            <ProgressBar value={current.cpuPercent} max={100} color="bg-blue-500" />
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Memory</span>
              <span className="font-mono">{current.memoryMb}/{limits.memoryMb} MB</span>
            </div>
            <ProgressBar value={current.memoryMb} max={limits.memoryMb} color="bg-green-500" />
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Disk</span>
              <span className="font-mono">{current.diskMb}/{limits.diskMb} MB</span>
            </div>
            <ProgressBar value={current.diskMb} max={limits.diskMb} color="bg-purple-500" />
          </div>
          <div className="flex gap-4 text-xs text-gray-500">
            <span>🌐 {(current.networkBytes / 1024).toFixed(0)} KB</span>
            <span>🔌 {current.activeConnections} conn</span>
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-500">No data available.</p>
      )}

      {alerts.length > 0 && (
        <div className="space-y-1">
          <span className="text-sm font-medium">Alerts</span>
          {alerts.slice(-5).map((a) => (
            <div key={a.id} className={`text-xs rounded border-l-4 p-2 ${alertColors[a.level]}`}>
              {a.message}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
