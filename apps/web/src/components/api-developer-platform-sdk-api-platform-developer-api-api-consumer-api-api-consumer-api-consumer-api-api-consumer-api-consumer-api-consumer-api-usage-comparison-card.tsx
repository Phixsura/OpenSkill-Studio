"use client";

interface Usage { consumerId: string; requests: number; errors: number; avgMs: number; }
interface Props { consumers: Usage[]; highestUsage: string; totalRequests: number; avgRequests: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiUsageComparisonCard({ consumers, highestUsage, totalRequests, avgRequests, appName }: Props) {
  const max = Math.max(...consumers.map((c) => c.requests), 1);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Usage Comparison</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {totalRequests.toLocaleString()} total · avg {avgRequests.toLocaleString()}</p>
      </div>
      {consumers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage data</p>
      ) : (
        <div className="space-y-1.5">
          {consumers.slice(0, 8).map((c) => (
            <div key={c.consumerId}>
              <div className="flex justify-between text-[11px]">
                <span className={`text-gray-700 dark:text-gray-300 ${c.consumerId === highestUsage ? "font-bold" : ""}`}>{c.consumerId}{c.consumerId === highestUsage ? " 👑" : ""}</span>
                <span className="text-gray-400">{c.requests.toLocaleString()} req</span>
              </div>
              <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-blue-500" style={{ width: `${(c.requests / max) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
