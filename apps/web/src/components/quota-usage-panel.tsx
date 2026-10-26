"use client";

interface ResourceQuota {
  resource: string;
  state: "ok" | "warning" | "exceeded" | "blocked";
  current: number;
  softLimit: number;
  hardLimit: number;
  usagePercent: number;
}

const stateConfig: Record<string, { color: string; barColor: string }> = {
  ok: { color: "text-green-600", barColor: "bg-green-500" },
  warning: { color: "text-yellow-600", barColor: "bg-yellow-500" },
  exceeded: { color: "text-red-600", barColor: "bg-red-500" },
  blocked: { color: "text-red-800", barColor: "bg-red-700" },
};

const resourceLabels: Record<string, { icon: string; unit: string }> = {
  storage_mb: { icon: "💾", unit: "MB" },
  compute_seconds: { icon: "⚙️", unit: "s" },
  api_calls: { icon: "📡", unit: "calls" },
  bandwidth_mb: { icon: "🌐", unit: "MB" },
  concurrent_connections: { icon: "🔌", unit: "conn" },
};

export function QuotaUsagePanel({
  quotas,
  extensionName,
  onReset,
}: {
  quotas: ResourceQuota[];
  extensionName: string;
  onReset?: (resource: string) => void;
}) {
  const issues = quotas.filter((q) => q.state !== "ok").length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📏 {extensionName} Quotas</h2>
        {issues > 0 && (
          <span className="text-xs bg-yellow-500 text-white px-2 py-0.5 rounded-full">{issues} issues</span>
        )}
      </div>

      <div className="space-y-3">
        {quotas.map((q) => {
          const cfg = stateConfig[q.state] || stateConfig.ok;
          const res = resourceLabels[q.resource] || { icon: "📦", unit: "" };
          return (
            <div key={q.resource} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span>{res.icon}</span>
                  <span className="font-semibold text-sm capitalize">{q.resource.replace(/_/g, " ")}</span>
                  <span className={`text-xs font-bold ${cfg.color}`}>{q.state}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">
                    {q.current} / {q.hardLimit} {res.unit}
                  </span>
                  {q.state !== "ok" && onReset && (
                    <button onClick={() => onReset(q.resource)}
                      className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">Reset</button>
                  )}
                </div>
              </div>
              <div className="relative h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                <div className={`absolute left-0 top-0 h-full rounded-full ${cfg.barColor} transition-all`}
                  style={{ width: `${Math.min(q.usagePercent, 100)}%` }} />
                {/* Soft limit marker */}
                <div className="absolute top-0 h-full w-0.5 bg-yellow-400"
                  style={{ left: `${(q.softLimit / q.hardLimit) * 100}%` }} />
              </div>
              <div className="flex justify-between text-xs text-gray-400 mt-0.5">
                <span>0</span>
                <span>soft: {q.softLimit}</span>
                <span>hard: {q.hardLimit}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
