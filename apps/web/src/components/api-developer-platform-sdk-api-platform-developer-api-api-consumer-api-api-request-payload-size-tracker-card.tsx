"use client";

interface SizeInfo { endpoint: string; method: string; avg_request_kb: number; avg_response_kb: number; total_transfer_mb: number; }
interface Props { stats: SizeInfo[]; totalTransferMb: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestPayloadSizeTrackerCard({ stats, totalTransferMb, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📏 Payload Sizes</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{totalTransferMb} MB</span>
      </div>
      {stats.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No payload data</p>
      ) : (
        <div className="space-y-1">
          {stats.map((s) => (
            <div key={`${s.method}-${s.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.method} {s.endpoint}</span>
              <span className="text-gray-400">↑{s.avg_request_kb}KB ↓{s.avg_response_kb}KB</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
