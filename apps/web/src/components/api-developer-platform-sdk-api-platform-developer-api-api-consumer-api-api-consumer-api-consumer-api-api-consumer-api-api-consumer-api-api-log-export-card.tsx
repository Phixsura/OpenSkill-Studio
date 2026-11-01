"use client";

interface Job { id: string; format: string; recordCount: number; status: string; startTime: string; endTime: string; }
interface Props { jobs: Job[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiLogExportCard({ jobs, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📤 Log Export</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {jobs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No exports</p>
      ) : (
        <div className="space-y-1">
          {jobs.map((j) => (
            <div key={j.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800">
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">{j.format.toUpperCase()}</span>
                <span className="ml-1 text-[10px] text-gray-400">{j.recordCount} records</span>
              </div>
              <span className={j.status === "completed" ? "text-green-500" : "text-amber-500"}>{j.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
