"use client";

interface Schedule { id: string; dataType: string; format: string; frequency: string; enabled: boolean; lastRun: string | null; }
interface Props { schedules: Schedule[]; consumerId: string; appName: string; }

const freqColors: Record<string, string> = {
  hourly: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  daily: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  weekly: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  monthly: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
};

export default function APIDeveloperPlatformSDKConsumerDataExportSchedulerCard({ schedules, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📤 Export Scheduler</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {schedules.filter(s => s.enabled).length} active</p>
      </div>
      {schedules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No export schedules</p>
      ) : (
        <div className="space-y-1">
          {schedules.map((s) => (
            <div key={s.id} className={`flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800 ${!s.enabled ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1">
                <span className="text-gray-700 dark:text-gray-300">{s.dataType}</span>
                <span className="rounded bg-gray-200 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-700">{s.format}</span>
                <span className={`rounded px-1 py-0.5 text-[9px] ${freqColors[s.frequency] ?? ""}`}>{s.frequency}</span>
              </div>
              <span className={s.enabled ? "text-green-500" : "text-gray-400"}>{s.enabled ? "ON" : "OFF"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
