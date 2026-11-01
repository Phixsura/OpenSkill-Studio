"use client";

interface ScheduleInfo { endpoint: string; method: string; phase: string; replacement: string; active_consumers: number; days_until_sunset: number; }
interface Props { schedules: ScheduleInfo[]; overdueCount: number; appName: string; }

const phaseColor: Record<string, string> = { announced: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400", warning: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400", sunset: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400", removed: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDeprecationSchedulerCard({ schedules, overdueCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📅 Deprecation Schedule</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {schedules.length} endpoints</p>
        </div>
        {overdueCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">⏰ {overdueCount} overdue</span>}
      </div>
      {schedules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No deprecations scheduled</p>
      ) : (
        <div className="space-y-1.5">
          {schedules.map((s) => (
            <div key={`${s.method}-${s.endpoint}`} className="text-[11px]">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <span className="font-mono text-gray-500">{s.method}</span>
                  <span className="text-gray-700 dark:text-gray-300">{s.endpoint}</span>
                </div>
                <span className={`rounded px-1 py-0.5 text-[9px] font-medium ${phaseColor[s.phase] ?? ""}`}>{s.phase}</span>
              </div>
              <div className="flex justify-between text-[10px] text-gray-400">
                <span>{s.active_consumers} consumers</span>
                <span>{s.days_until_sunset > 0 ? `${s.days_until_sunset}d left` : "overdue"}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
