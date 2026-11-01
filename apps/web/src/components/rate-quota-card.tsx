"use client";

interface TierInfo {
  tier: string;
  isCurrent: boolean;
  requests_per_day: number;
  requests_per_minute: number;
  storage_mb: number;
  webhooks: number;
}

interface RateQuotaCardProps {
  tiers: TierInfo[];
  appName: string;
  currentTier: string;
}

const TIER_COLORS: Record<string, string> = {
  free: "border-gray-300 dark:border-gray-600",
  starter: "border-blue-400 dark:border-blue-500",
  pro: "border-purple-400 dark:border-purple-500",
  enterprise: "border-yellow-400 dark:border-yellow-500",
};

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(0)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
  return n.toString();
}

export default function RateQuotaCard({ tiers, appName, currentTier }: RateQuotaCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Rate Quotas</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium capitalize text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
          {currentTier}
        </span>
      </div>

      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {tiers.map((t) => {
          const borderColor = TIER_COLORS[t.tier] ?? TIER_COLORS.free;
          return (
            <div
              key={t.tier}
              className={`rounded-lg border-2 px-3 py-2.5 ${borderColor} ${
                t.isCurrent ? "bg-blue-50/50 dark:bg-blue-950/20" : ""
              }`}
            >
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm font-medium capitalize text-gray-800 dark:text-gray-200">
                  {t.tier}
                </span>
                {t.isCurrent && (
                  <span className="text-[10px] text-blue-600 dark:text-blue-400">Current</span>
                )}
              </div>
              <div className="grid grid-cols-2 gap-1 text-[11px]">
                <div>
                  <span className="text-gray-400">Daily:</span>{" "}
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    {formatNum(t.requests_per_day)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-400">Per min:</span>{" "}
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    {formatNum(t.requests_per_minute)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-400">Storage:</span>{" "}
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    {formatNum(t.storage_mb)} MB
                  </span>
                </div>
                <div>
                  <span className="text-gray-400">Webhooks:</span>{" "}
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    {formatNum(t.webhooks)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
