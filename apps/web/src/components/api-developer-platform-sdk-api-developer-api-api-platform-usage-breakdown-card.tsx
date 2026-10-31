"use client";

interface BreakdownInfo { period: string; api_calls: number; webhook_deliveries: number; storage_mb: number; bandwidth_gb: number; active_consumers: number; total_operations: number; cost_weighted_score: number; }
interface Props { breakdowns: BreakdownInfo[]; totalOperations: number; appName: string; }

export default function APIDeveloperPlatformSDKApiDeveloperApiApiPlatformUsageBreakdownCard({ breakdowns, totalOperations, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Usage Breakdown</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-blue-600">{totalOperations.toLocaleString()} ops</span>
      </div>
      {breakdowns.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage data</p>
      ) : (
        <div className="space-y-2">
          {breakdowns.map((b) => (
            <div key={b.period} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{b.period}</span>
                <span className="text-gray-400">{b.total_operations.toLocaleString()} ops</span>
              </div>
              <div className="mt-0.5 grid grid-cols-3 gap-1 text-[9px] text-gray-400">
                <span>API: {b.api_calls.toLocaleString()}</span>
                <span>WH: {b.webhook_deliveries.toLocaleString()}</span>
                <span>Score: {b.cost_weighted_score}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
