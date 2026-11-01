"use client";

interface Bucket { statusCode: number; errorCode: string; count: number; percentage: number; }
interface Props { endpoint: string; totalErrors: number; errorRate: number; buckets: Bucket[]; mostCommon: string; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiEndpointErrorDistributionCard({ endpoint, totalErrors, errorRate, buckets, mostCommon, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Error Distribution</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — <code>{endpoint}</code> · {totalErrors} errors ({errorRate}%)</p>
      </div>
      {buckets.length === 0 ? (
        <p className="text-center text-sm text-green-500">No errors!</p>
      ) : (
        <div className="space-y-1.5">
          {buckets.slice(0, 6).map((b) => (
            <div key={`${b.statusCode}-${b.errorCode}`}>
              <div className="flex justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300"><span className="text-red-500">{b.statusCode}</span> {b.errorCode}{b.errorCode === mostCommon ? " 🔴" : ""}</span>
                <span className="text-gray-400">{b.count} ({b.percentage}%)</span>
              </div>
              <div className="mt-0.5 h-1 rounded-full bg-gray-200 dark:bg-gray-700"><div className="h-full rounded-full bg-red-400" style={{ width: `${b.percentage}%` }} /></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
