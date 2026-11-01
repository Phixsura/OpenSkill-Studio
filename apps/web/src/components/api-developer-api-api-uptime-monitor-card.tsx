"use client";

interface RecordInfo { endpoint: string; uptime_pct: number; total_downtime_minutes: number; }
interface Props { records: RecordInfo[]; belowThresholdCount: number; appName: string; }

export default function APIDeveloperAPIApiUptimeMonitorCard({ records, belowThresholdCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏰ Uptime Monitor</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {belowThresholdCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{belowThresholdCount} below SLA</span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-[10px] text-green-700">all healthy</span>
        )}
      </div>
      {records.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No uptime data</p>
      ) : (
        <div className="space-y-1.5">
          {records.map((r) => (
            <div key={r.endpoint} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{r.endpoint}</span>
              <div className="flex gap-2">
                <span className={r.uptime_pct >= 99.9 ? "text-green-600 font-bold" : "text-red-500 font-bold"}>{r.uptime_pct}%</span>
                {r.total_downtime_minutes > 0 && <span className="text-gray-400">{r.total_downtime_minutes}m down</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
