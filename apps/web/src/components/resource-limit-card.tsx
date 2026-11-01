"use client";

interface ResourceLimit { resource: string; limit: number; current: number; unlimited: boolean; }
interface ResourceLimitCardProps { plan: string; resources: ResourceLimit[]; onUpgrade: () => void; }

const resourceLabels: Record<string, string> = {
  cpu_cores: "CPU Cores", memory_mb: "Memory (MB)", storage_gb: "Storage (GB)", bandwidth_gb: "Bandwidth (GB)",
};

export function ResourceLimitCard({ plan, resources, onUpgrade }: ResourceLimitCardProps) {
  const hasViolation = resources.some(r => !r.unlimited && r.current > r.limit);
  return (
    <div className="space-y-3 rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Resource Limits</h3>
        <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium capitalize text-blue-700 dark:bg-blue-900/30">{plan}</span>
      </div>
      <div className="space-y-2">
        {resources.map(r => {
          const pct = r.unlimited ? 0 : Math.min(Math.round((r.current / Math.max(r.limit, 1)) * 100), 100);
          const over = !r.unlimited && r.current > r.limit;
          return (
            <div key={r.resource}>
              <div className="flex justify-between text-xs">
                <span>{resourceLabels[r.resource] ?? r.resource}</span>
                <span className="text-gray-400">{r.unlimited ? `${r.current} / ∞` : `${r.current} / ${r.limit}`}</span>
              </div>
              {!r.unlimited && (
                <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div className={`h-full rounded-full ${over ? "bg-red-500" : "bg-green-500"}`}
                    style={{ width: `${pct}%` }} />
                </div>
              )}
            </div>
          );
        })}
      </div>
      {hasViolation && (
        <button onClick={onUpgrade} className="w-full rounded bg-blue-600 py-1.5 text-sm text-white">Upgrade Plan</button>
      )}
    </div>
  );
}
