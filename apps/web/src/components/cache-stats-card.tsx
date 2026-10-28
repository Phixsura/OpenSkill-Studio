"use client";

interface CacheStatsInfo {
  hits: number;
  misses: number;
  evictions: number;
  size: number;
  max_size: number;
  hit_rate: number;
  namespaces: { installation_id: string; entry_count: number }[];
}

interface CacheStatsCardProps {
  stats: CacheStatsInfo;
  appName: string;
}

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

function HitRateRing({ pct }: { pct: number }) {
  const r = 32;
  const c = 2 * Math.PI * r;
  const offset = c - (Math.min(pct, 100) / 100) * c;
  const color = pct >= 90 ? "stroke-green-500" : pct >= 70 ? "stroke-yellow-500" : "stroke-red-500";
  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="76" height="76" className="-rotate-90">
        <circle
          cx="38"
          cy="38"
          r={r}
          fill="none"
          strokeWidth="5"
          className="stroke-gray-200 dark:stroke-gray-700"
        />
        <circle
          cx="38"
          cy="38"
          r={r}
          fill="none"
          strokeWidth="5"
          strokeDasharray={c}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={color}
        />
      </svg>
      <div className="absolute text-center">
        <p className="text-sm font-bold text-gray-800 dark:text-gray-200">{pct.toFixed(0)}%</p>
        <p className="text-[8px] text-gray-400">hit rate</p>
      </div>
    </div>
  );
}

function StatBox({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="text-center">
      <p className={`text-lg font-bold ${color ?? "text-gray-800 dark:text-gray-200"}`}>{value}</p>
      <p className="text-[10px] text-gray-500">{label}</p>
    </div>
  );
}

function UsageBar({ size, max }: { size: number; max: number }) {
  const pct = max > 0 ? Math.min((size / max) * 100, 100) : 0;
  const color = pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-yellow-500" : "bg-blue-500";
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[11px] text-gray-500">
        <span>Capacity</span>
        <span>
          {formatNumber(size)} / {formatNumber(max)}
        </span>
      </div>
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-2 rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function CacheStatsCard({ stats, appName }: CacheStatsCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Cache Stats</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
      </div>

      <div className="mb-4 flex items-center justify-center gap-6">
        <HitRateRing pct={stats.hit_rate} />
        <div className="flex gap-5">
          <StatBox
            label="Hits"
            value={formatNumber(stats.hits)}
            color="text-green-600 dark:text-green-400"
          />
          <StatBox
            label="Misses"
            value={formatNumber(stats.misses)}
            color="text-red-600 dark:text-red-400"
          />
          <StatBox label="Evictions" value={formatNumber(stats.evictions)} />
        </div>
      </div>

      <UsageBar size={stats.size} max={stats.max_size} />

      {stats.namespaces.length > 0 && (
        <div className="mt-3 border-t border-gray-100 pt-3 dark:border-gray-800">
          <p className="mb-1.5 text-xs font-medium text-gray-500">Namespaces</p>
          <div className="flex flex-wrap gap-2">
            {stats.namespaces.map((ns) => (
              <span
                key={ns.installation_id}
                className="rounded bg-gray-100 px-2 py-0.5 text-[11px] text-gray-600 dark:bg-gray-800 dark:text-gray-400"
              >
                {ns.installation_id}: {ns.entry_count}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
