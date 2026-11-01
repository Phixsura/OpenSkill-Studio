"use client";

interface BackoffInfo { consumer_id: string; endpoint: string; attempt: number; current_delay_s: number; max_delay_s: number; }
interface Props { states: BackoffInfo[]; backedOffCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookBackoffCard({ states, backedOffCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏳ Webhook Backoff</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {backedOffCount > 0 && <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">{backedOffCount} backing off</span>}
      </div>
      {states.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No backoff states</p>
      ) : (
        <div className="space-y-1">
          {states.map((s) => (
            <div key={`${s.consumer_id}-${s.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
              <span className={s.attempt > 0 ? "text-amber-600 dark:text-amber-400" : "text-gray-400"}>{s.current_delay_s}s · attempt {s.attempt}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
