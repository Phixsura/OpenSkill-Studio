"use client";

interface Quota { resource: string; current: number; max: number; }
interface Props { quotas: Quota[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiResourceQuotaCard({ quotas, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Resource Quotas</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {quotas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No quotas set</p>
      ) : (
        <div className="space-y-2">
          {quotas.map((q) => {
            const pct = q.max > 0 ? Math.round((q.current / q.max) * 100) : 0;
            return (
              <div key={q.resource}>
                <div className="flex justify-between text-[11px]">
                  <span className="text-gray-700 dark:text-gray-300">{q.resource}</span>
                  <span className="text-gray-400">{q.current}/{q.max}</span>
                </div>
                <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div className={`h-full rounded-full ${pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-amber-500" : "bg-blue-500"}`} style={{ width: `${Math.min(pct, 100)}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
