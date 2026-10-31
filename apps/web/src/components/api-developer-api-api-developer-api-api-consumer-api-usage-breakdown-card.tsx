"use client";

interface EndpointInfo { endpoint: string; method: string; call_count: number; error_count: number; }
interface BreakdownInfo { consumer_id: string; total_calls: number; total_errors: number; unique_endpoints: number; endpoints: EndpointInfo[]; }
interface Props { breakdowns: BreakdownInfo[]; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiConsumerApiUsageBreakdownCard({ breakdowns, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Usage Breakdown</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {breakdowns.length} consumers</p>
      </div>
      {breakdowns.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage data</p>
      ) : (
        <div className="space-y-2">
          {breakdowns.slice(0, 5).map((b) => (
            <div key={b.consumer_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{b.consumer_id}</span>
                <span className="text-gray-400">{b.total_calls.toLocaleString()} calls · {b.unique_endpoints} endpoints</span>
              </div>
              {b.total_errors > 0 && <p className="text-[10px] text-red-500">{b.total_errors} errors</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
