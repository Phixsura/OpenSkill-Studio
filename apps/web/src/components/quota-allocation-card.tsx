"use client";

interface QuotaInfo {
  resource: string;
  limit: number;
  used: number;
  unit: string;
}

interface QuotaAllocationCardProps {
  quotas: QuotaInfo[];
  appName: string;
}

export default function QuotaAllocationCard({ quotas, appName }: QuotaAllocationCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📊 Quota Allocation
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{quotas.length} quotas</span>
      </div>

      {quotas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No quotas configured</p>
      ) : (
        <div className="space-y-3">
          {quotas.map((q) => {
            const pct = q.limit > 0 ? Math.round((q.used / q.limit) * 100) : 100;
            const barColor =
              pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-yellow-500" : "bg-green-500";
            return (
              <div key={q.resource}>
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-gray-700 dark:text-gray-300">{q.resource}</span>
                  <span className="text-gray-400">
                    {q.used.toLocaleString()} / {q.limit.toLocaleString()} {q.unit}
                  </span>
                </div>
                <div className="mt-1 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                  <div
                    className={`h-1.5 rounded-full ${barColor}`}
                    style={{ width: `${Math.min(100, pct)}%` }}
                  />
                </div>
                <p className="mt-0.5 text-right text-[10px] text-gray-400">{pct}%</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
