"use client";

interface Schedule { keyId: string; intervalDays: number; daysUntil: number; due: boolean; notify: boolean; autoRotate: boolean; }
interface Props { schedules: Schedule[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyRotationScheduleCard({ schedules, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Key Rotation Schedule</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {schedules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rotation schedules</p>
      ) : (
        <div className="space-y-1">
          {schedules.map((s) => (
            <div key={s.keyId} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800">
              <div>
                <code className="text-gray-700 dark:text-gray-300">{s.keyId}</code>
                <span className="ml-1 text-[10px] text-gray-400">every {s.intervalDays}d</span>
                {s.autoRotate && <span className="ml-1 text-[9px] text-blue-400">auto</span>}
              </div>
              <span className={`text-[10px] font-medium ${s.due ? "text-red-500" : s.notify ? "text-amber-500" : "text-green-500"}`}>
                {s.due ? "DUE NOW" : s.notify ? `${s.daysUntil}d ⚠` : `${s.daysUntil}d`}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
