"use client";

interface QuotaSummary {
  metric: string;
  used: number;
  limit: number;
  pct: number;
}

interface APIUsageQuotaCardProps {
  quotas: QuotaSummary[];
  period: string;
  appName: string;
}

export default function APIUsageQuotaCard({ quotas, period, appName }: APIUsageQuotaCardProps) {
  const overages = quotas.filter((q) => q.used > q.limit).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📊 Usage Quotas
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {appName} · {period}
          </p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{quotas.length} metrics</span>
          {overages > 0 && <p className="text-[10px] text-red-500">{overages} over limit</p>}
        </div>
      </div>

      {quotas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage quotas</p>
      ) : (
        <div className="space-y-3">
          {quotas.map((q) => {
            const over = q.used > q.limit;
            const barColor = over ? "bg-red-500" : q.pct >= 80 ? "bg-yellow-500" : "bg-green-500";
            return (
              <div key={q.metric}>
                <div className="flex justify-between text-xs">
                  <span className="font-medium text-gray-700 dark:text-gray-300">{q.metric}</span>
                  <span className={`${over ? "font-medium text-red-500" : "text-gray-400"}`}>
                    {q.used.toLocaleString()} / {q.limit.toLocaleString()}
                  </span>
                </div>
                <div className="mt-1 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                  <div
                    className={`h-1.5 rounded-full ${barColor}`}
                    style={{ width: `${Math.min(100, q.pct)}%` }}
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
