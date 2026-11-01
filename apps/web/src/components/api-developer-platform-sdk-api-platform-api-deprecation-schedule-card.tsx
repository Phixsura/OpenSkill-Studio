"use client";

interface ScheduleInfo { endpoint: string; version: string; sunset_at: string; replacement: string; active_consumers: number; migration_pct: number; urgency: string; }
interface Props { schedules: ScheduleInfo[]; criticalCount: number; appName: string; }

const uColor: Record<string, string> = { critical: "bg-red-100 text-red-700", high: "bg-orange-100 text-orange-700", medium: "bg-yellow-100 text-yellow-700", low: "bg-green-100 text-green-700", done: "bg-gray-100 text-gray-500" };

export default function APIDeveloperPlatformSDKApiPlatformApiDeprecationScheduleCard({ schedules, criticalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📅 Deprecation Schedule</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {criticalCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{criticalCount} critical</span>}
      </div>
      {schedules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No deprecation schedules</p>
      ) : (
        <div className="space-y-2">
          {schedules.map((s) => (
            <div key={`${s.version}-${s.endpoint}`} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className={`rounded px-1 py-0.5 text-[9px] ${uColor[s.urgency] ?? ""}`}>{s.urgency}</span>
                  <span className="text-gray-700 dark:text-gray-300">{s.endpoint}</span>
                </div>
                <span className="text-gray-400">sunset: {s.sunset_at}</span>
              </div>
              <div className="mt-1 h-1.5 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-1.5 rounded-full bg-blue-500" style={{ width: `${s.migration_pct}%` }} />
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">{s.migration_pct}% migrated · {s.active_consumers} remaining{s.replacement ? ` → ${s.replacement}` : ""}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
