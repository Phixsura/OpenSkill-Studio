"use client";

interface QuotaInfo {
  resource: string;
  used: number;
  limit: number;
  usage_pct: number;
  exceeded: boolean;
}

interface ResourceQuotaCardProps {
  quotas: QuotaInfo[];
  appName: string;
}

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  if (n % 1 !== 0) return n.toFixed(1);
  return n.toString();
}

export default function ResourceQuotaCard({ quotas, appName }: ResourceQuotaCardProps) {
  const exceededCount = quotas.filter((q) => q.exceeded).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Resource Quotas
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {exceededCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {exceededCount} exceeded
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            Within limits
          </span>
        )}
      </div>

      {quotas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No quotas configured</p>
      ) : (
        <div className="space-y-3">
          {quotas.map((q) => {
            const barColor = q.exceeded
              ? "bg-red-500"
              : q.usage_pct >= 80
                ? "bg-yellow-500"
                : "bg-green-500";
            return (
              <div key={q.resource}>
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="text-gray-700 dark:text-gray-300">
                    {q.resource.replace(/_/g, " ")}
                  </span>
                  <span className="text-gray-500">
                    {formatNum(q.used)} / {formatNum(q.limit)}
                  </span>
                </div>
                <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div
                    className={`h-2 rounded-full ${barColor}`}
                    style={{ width: `${Math.min(q.usage_pct, 100)}%` }}
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
