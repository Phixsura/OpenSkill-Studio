"use client";

interface QuotaInfo { consumer_id: string; daily_limit: number; daily_used: number; remaining: number; exhausted: boolean; }
interface APIConsumerQuotaCardProps { quotas: QuotaInfo[]; appName: string; }

export default function APIConsumerQuotaCard({ quotas, appName }: APIConsumerQuotaCardProps) {
  const exhaustedCount = quotas.filter((q) => q.exhausted).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Consumer Quotas</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{quotas.length} consumers</span>
          {exhaustedCount > 0 && <p className="text-[10px] text-red-500">{exhaustedCount} exhausted</p>}
        </div>
      </div>
      {quotas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No consumer quotas</p>
      ) : (
        <div className="space-y-2">
          {quotas.map((q) => {
            const pct = q.daily_limit > 0 ? Math.round((q.daily_used / q.daily_limit) * 100) : 0;
            const barColor = q.exhausted ? "bg-red-500" : pct >= 80 ? "bg-yellow-500" : "bg-green-500";
            return (
              <div key={q.consumer_id}>
                <div className="flex justify-between text-[11px]">
                  <span className="text-gray-700 dark:text-gray-300">{q.consumer_id}</span>
                  <span className="text-gray-400">{q.daily_used}/{q.daily_limit}</span>
                </div>
                <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                  <div className={`h-1 rounded-full ${barColor}`} style={{ width: `${Math.min(100, pct)}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
