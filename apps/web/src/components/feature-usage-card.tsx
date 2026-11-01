"use client";

interface FeatureUsageInfo {
  feature_id: string;
  unique_users: number;
  total_uses: number;
  adoption_pct: number;
}

interface FeatureUsageCardProps {
  features: FeatureUsageInfo[];
  totalUsers: number;
  appName: string;
}

function formatNum(n: number): string {
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function FeatureUsageCard({ features, totalUsers, appName }: FeatureUsageCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Feature Usage</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {totalUsers} users · {features.length} features
        </span>
      </div>

      {features.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No feature usage data</p>
      ) : (
        <div className="space-y-2">
          {features.map((f) => {
            const barColor =
              f.adoption_pct >= 75
                ? "bg-green-500"
                : f.adoption_pct >= 25
                  ? "bg-blue-500"
                  : "bg-yellow-500";
            return (
              <div key={f.feature_id}>
                <div className="mb-0.5 flex items-center justify-between text-xs">
                  <span className="text-gray-700 dark:text-gray-300">
                    {f.feature_id.replace(/_/g, " ")}
                  </span>
                  <span className="text-gray-500">
                    {f.adoption_pct}% · {formatNum(f.total_uses)} uses
                  </span>
                </div>
                <div className="h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div
                    className={`h-1.5 rounded-full ${barColor}`}
                    style={{ width: `${Math.min(f.adoption_pct, 100)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
