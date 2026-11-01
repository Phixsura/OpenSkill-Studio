"use client";

interface Allocation {
  alloc_id: string;
  entity_id: string;
  entity_type: string;
  reserved: number;
  used: number;
  usage_pct: number;
}

interface PoolSummary {
  org_id: string;
  quota_type: string;
  total: number;
  reserved: number;
  used: number;
  available: number;
  utilization_pct: number;
  allocations: Allocation[];
}

interface QuotaUsageDashboardProps {
  pools: PoolSummary[];
  orgName: string;
}

const TYPE_LABELS: Record<string, { label: string; unit: string; icon: string }> = {
  requests: { label: "API Requests", unit: "", icon: "📡" },
  bandwidth_mb: { label: "Bandwidth", unit: "MB", icon: "📶" },
  storage_mb: { label: "Storage", unit: "MB", icon: "💾" },
  compute_seconds: { label: "Compute", unit: "s", icon: "⚡" },
};

function formatValue(value: number, unit: string): string {
  if (unit === "MB" && value >= 1024) return `${(value / 1024).toFixed(1)} GB`;
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return `${value}${unit ? ` ${unit}` : ""}`;
}

function barColor(pct: number): string {
  if (pct >= 90) return "bg-red-500";
  if (pct >= 70) return "bg-yellow-500";
  return "bg-blue-500";
}

function PoolCard({ pool }: { pool: PoolSummary }) {
  const meta = TYPE_LABELS[pool.quota_type] ?? { label: pool.quota_type, unit: "", icon: "📊" };
  const pct = pool.utilization_pct;

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">{meta.icon}</span>
          <h4 className="text-sm font-semibold">{meta.label}</h4>
        </div>
        <span
          className={`text-sm font-bold ${pct >= 90 ? "text-red-600" : pct >= 70 ? "text-yellow-600" : "text-gray-700 dark:text-gray-300"}`}
        >
          {pct.toFixed(1)}%
        </span>
      </div>

      {/* Overall bar */}
      <div className="mt-2">
        <div className="flex justify-between text-xs text-gray-500">
          <span>{formatValue(pool.used, meta.unit)} used</span>
          <span>{formatValue(pool.total, meta.unit)} total</span>
        </div>
        <div className="mt-1 h-2.5 rounded-full bg-gray-200 dark:bg-gray-700">
          <div
            className={`h-full rounded-full ${barColor(pct)}`}
            style={{ width: `${Math.min(pct, 100)}%` }}
          />
        </div>
        <div className="mt-1 flex justify-between text-[10px] text-gray-400">
          <span>{formatValue(pool.reserved, meta.unit)} reserved</span>
          <span>{formatValue(pool.available, meta.unit)} available</span>
        </div>
      </div>

      {/* Allocations */}
      {pool.allocations.length > 0 && (
        <div className="mt-3 space-y-1.5">
          <p className="text-[10px] font-semibold uppercase text-gray-400">Allocations</p>
          {pool.allocations.map((a) => (
            <div key={a.alloc_id} className="flex items-center gap-2 text-xs">
              <span className="w-20 truncate font-medium">{a.entity_id}</span>
              <div className="h-1.5 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
                <div
                  className={`h-full rounded-full ${barColor(a.usage_pct)}`}
                  style={{ width: `${Math.min(a.usage_pct, 100)}%` }}
                />
              </div>
              <span className="w-16 text-right text-gray-500">
                {formatValue(a.used, meta.unit)}/{formatValue(a.reserved, meta.unit)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function QuotaUsageDashboard({ pools, orgName }: QuotaUsageDashboardProps) {
  const totalUsed = pools.reduce((s, p) => s + p.used, 0);
  const totalQuota = pools.reduce((s, p) => s + p.total, 0);
  const overallPct = totalQuota > 0 ? (totalUsed / totalQuota) * 100 : 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Quota Usage</h2>
          <p className="text-xs text-gray-500">
            {orgName} • {pools.length} quota pools
          </p>
        </div>
        <div className="text-right">
          <p
            className={`text-lg font-bold ${overallPct >= 80 ? "text-red-600" : "text-gray-700 dark:text-gray-300"}`}
          >
            {overallPct.toFixed(1)}%
          </p>
          <p className="text-[10px] text-gray-400">overall utilization</p>
        </div>
      </div>

      {pools.length === 0 ? (
        <div className="rounded-lg border border-gray-200 py-8 text-center dark:border-gray-700">
          <span className="text-3xl">📊</span>
          <p className="mt-2 text-sm text-gray-500">No quota pools configured</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {pools.map((p) => (
            <PoolCard key={`${p.org_id}-${p.quota_type}`} pool={p} />
          ))}
        </div>
      )}
    </div>
  );
}
