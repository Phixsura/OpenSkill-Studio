"use client";

interface Meter { metric: string; total: number; count: number; }
interface Props { consumerId: string; meters: Meter[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerBillingMeterCard({ consumerId, meters, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💰 Billing Meter</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {meters.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage recorded</p>
      ) : (
        <div className="space-y-2">
          {meters.map((m) => (
            <div key={m.metric} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div>
                <div className="text-[11px] font-medium text-gray-700 dark:text-gray-300">{m.metric}</div>
                <div className="text-[10px] text-gray-400">{m.count} events</div>
              </div>
              <div className="text-sm font-bold text-gray-900 dark:text-gray-100">{m.total.toLocaleString()}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
