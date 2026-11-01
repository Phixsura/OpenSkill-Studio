"use client";

interface ErrorInfo { id: string; statusCode: number; errorCode: string; message: string; timestamp: string; }
interface Summary { endpoint: string; totalErrors: number; errorRate: number; mostCommon: string; byStatus: Record<string, number>; }
interface Props { summary: Summary; recentErrors: ErrorInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiConsumerApiEndpointErrorTrackerCard({ summary, recentErrors, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔴 Error Tracker</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — <code>{summary.endpoint}</code></p>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="rounded bg-red-50 p-1.5 dark:bg-red-900/20"><div className="font-bold text-red-600">{summary.totalErrors}</div><div className="text-[9px] text-gray-400">Errors</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className={`font-bold ${summary.errorRate > 5 ? "text-red-600" : "text-green-600"}`}>{summary.errorRate}%</div><div className="text-[9px] text-gray-400">Error Rate</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{summary.mostCommon || "—"}</div><div className="text-[9px] text-gray-400">Top Error</div></div>
      </div>
      {recentErrors.length > 0 && (
        <div className="space-y-0.5">
          {recentErrors.slice(0, 5).map((e) => (
            <div key={e.id} className="flex items-center justify-between text-[10px]">
              <div className="flex gap-1"><span className="text-red-500">{e.statusCode}</span><code className="text-gray-500">{e.errorCode}</code></div>
              <span className="text-gray-400">{e.timestamp}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
