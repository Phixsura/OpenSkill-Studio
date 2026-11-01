"use client";

interface PoolStatus {
  resource: string;
  total: number;
  allocated: number;
  reserved: number;
  available: number;
  utilizationPct: number;
  queued: number;
}

const resourceIcons: Record<string, string> = {
  cpu: "🔲", memory: "🧠", gpu: "🎮", disk_io: "💿",
};

const resourceUnits: Record<string, string> = {
  cpu: "cores", memory: "GB", gpu: "units", disk_io: "IOPS",
};

export function ResourcePoolPanel({
  pools,
  onRelease,
}: {
  pools: PoolStatus[];
  onRelease?: (resource: string) => void;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🏊 Resource Pools</h2>

      <div className="space-y-3">
        {pools.map((pool) => {
          const icon = resourceIcons[pool.resource] || "📦";
          const unit = resourceUnits[pool.resource] || "";
          const barColor = pool.utilizationPct > 90 ? "bg-red-500" : pool.utilizationPct > 70 ? "bg-yellow-500" : "bg-green-500";

          return (
            <div key={pool.resource} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{icon}</span>
                  <span className="font-semibold text-sm capitalize">{pool.resource.replace("_", " ")}</span>
                  {pool.queued > 0 && (
                    <span className="text-xs bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 px-1.5 py-0.5 rounded">
                      {pool.queued} queued
                    </span>
                  )}
                </div>
                <span className={`text-sm font-bold ${pool.utilizationPct > 90 ? "text-red-600" : pool.utilizationPct > 70 ? "text-yellow-600" : "text-green-600"}`}>
                  {pool.utilizationPct}%
                </span>
              </div>

              <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-2">
                <div className="h-full flex">
                  <div className={`${barColor} transition-all`} style={{ width: `${pool.utilizationPct}%` }} />
                  {pool.reserved > 0 && (
                    <div className="bg-blue-300 dark:bg-blue-700" style={{ width: `${(pool.reserved / pool.total) * 100}%` }} />
                  )}
                </div>
              </div>

              <div className="flex gap-4 text-xs text-gray-500">
                <span>Allocated: {pool.allocated}/{pool.total} {unit}</span>
                {pool.reserved > 0 && <span className="text-blue-500">Reserved: {pool.reserved}</span>}
                <span>Available: {pool.available}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
