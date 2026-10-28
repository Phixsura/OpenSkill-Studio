"use client";

interface SLIReportInfo {
  metric: string;
  current: number;
  average: number;
  target: number | null;
  meets_target: boolean;
  measurement_count: number;
}

interface SLITrackerCardProps {
  reports: SLIReportInfo[];
  appName: string;
}

export default function SLITrackerCard({ reports, appName }: SLITrackerCardProps) {
  const missingCount = reports.filter((r) => !r.meets_target).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">SLI Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {missingCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {missingCount} below target
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            All on target
          </span>
        )}
      </div>

      {reports.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SLI data</p>
      ) : (
        <div className="space-y-2">
          {reports.map((r) => (
            <div
              key={r.metric}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-800 dark:text-gray-200">
                  {r.metric.replace(/_/g, " ")}
                </span>
                <span
                  className={`text-xs font-medium ${r.meets_target ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}
                >
                  {r.current}
                </span>
              </div>
              <div className="mt-0.5 flex items-center gap-3 text-[11px] text-gray-400">
                <span>avg {r.average}</span>
                {r.target !== null && <span>target {r.target}</span>}
                <span>{r.measurement_count} measurements</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
