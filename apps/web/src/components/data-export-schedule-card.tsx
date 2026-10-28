"use client";

interface ExportScheduleInfo {
  schedule_id: string;
  resource_type: string;
  format: string;
  destination: string;
  interval_hours: number;
  enabled: boolean;
  run_count: number;
  last_error: string;
}

interface DataExportScheduleCardProps {
  schedules: ExportScheduleInfo[];
  appName: string;
}

export default function DataExportScheduleCard({
  schedules,
  appName,
}: DataExportScheduleCardProps) {
  const activeCount = schedules.filter((s) => s.enabled).length;
  const errorCount = schedules.filter((s) => s.last_error).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Export Schedules
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{activeCount} active</span>
          {errorCount > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {errorCount} errors
            </span>
          )}
        </div>
      </div>

      {schedules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No export schedules</p>
      ) : (
        <div className="space-y-2">
          {schedules.map((s) => (
            <div
              key={s.schedule_id}
              className={`rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!s.enabled ? "opacity-50" : ""}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2 w-2 rounded-full ${s.enabled ? "bg-green-500" : "bg-gray-300"}`}
                  />
                  <span className="text-sm text-gray-800 dark:text-gray-200">
                    {s.resource_type}
                  </span>
                  <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">
                    {s.format}
                  </span>
                </div>
                <span className="text-[11px] text-gray-400">
                  every {s.interval_hours}h · {s.run_count} runs
                </span>
              </div>
              <p className="mt-0.5 truncate font-mono text-[10px] text-gray-400">{s.destination}</p>
              {s.last_error && <p className="mt-0.5 text-[10px] text-red-500">{s.last_error}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
