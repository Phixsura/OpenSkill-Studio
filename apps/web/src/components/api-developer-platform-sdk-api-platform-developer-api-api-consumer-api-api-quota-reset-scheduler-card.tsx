"use client";

interface ScheduleInfo { consumer_id: string; interval: string; minutes_until_reset: number; total_resets: number; }
interface Props { schedules: ScheduleInfo[]; dueCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiQuotaResetSchedulerCard({ schedules, dueCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Quota Resets</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {schedules.length} schedules</p>
        </div>
        {dueCount > 0 && <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{dueCount} due</span>}
      </div>
      {schedules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No reset schedules</p>
      ) : (
        <div className="space-y-1">
          {schedules.map((s) => (
            <div key={s.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
              <span className="text-gray-400">{s.interval} · {s.minutes_until_reset}m · {s.total_resets}×</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
