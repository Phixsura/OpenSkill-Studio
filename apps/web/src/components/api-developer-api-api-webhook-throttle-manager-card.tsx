"use client";

interface ConfigInfo { destination: string; max_per_second: number; max_per_minute: number; throttled_count: number; }
interface Props { configs: ConfigInfo[]; appName: string; }

export default function APIDeveloperAPIApiWebhookThrottleManagerCard({ configs, appName }: Props) {
  const totalThrottled = configs.reduce((s, c) => s + c.throttled_count, 0);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Webhook Throttles</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {totalThrottled > 0 && <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] text-orange-700">{totalThrottled} throttled</span>}
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No throttle configs</p>
      ) : (
        <div className="space-y-1.5">
          {configs.map((c) => (
            <div key={c.destination} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{new URL(c.destination).hostname}</span>
              <span className="text-gray-400">{c.max_per_second}/s · {c.max_per_minute}/m</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
