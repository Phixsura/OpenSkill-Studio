"use client";

interface RecordInfo { consumer_id: string; unique_ip_count: number; total_requests: number; top_ip: string; }
interface Props { records: RecordInfo[]; suspiciousCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiConsumerIpTrackerCard({ records, suspiciousCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌐 Consumer IPs</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {suspiciousCount > 0 && <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] text-orange-700">{suspiciousCount} suspicious</span>}
      </div>
      {records.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No IP data</p>
      ) : (
        <div className="space-y-1">
          {records.slice(0, 5).map((r) => (
            <div key={r.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{r.consumer_id}</span>
              <span className="text-gray-400">{r.unique_ip_count} IPs · {r.total_requests} reqs</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
