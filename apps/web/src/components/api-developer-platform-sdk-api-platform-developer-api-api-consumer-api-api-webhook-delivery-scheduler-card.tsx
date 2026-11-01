"use client";

interface ScheduledInfo { delivery_id: string; consumer_id: string; minutes_until: number; delivered: boolean; }
interface Props { scheduled: ScheduledInfo[]; pendingCount: number; dueCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliverySchedulerCard({ scheduled, pendingCount, dueCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📅 Delivery Scheduler</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {pendingCount} pending</p>
        </div>
        {dueCount > 0 && <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{dueCount} due now</span>}
      </div>
      {scheduled.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No scheduled deliveries</p>
      ) : (
        <div className="space-y-1">
          {scheduled.map((s) => (
            <div key={s.delivery_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
              <span className={s.delivered ? "text-green-600 dark:text-green-400" : "text-gray-400"}>{s.delivered ? "✅" : `${s.minutes_until}m`}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
