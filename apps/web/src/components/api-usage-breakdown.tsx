"use client";

interface BreakdownItem { endpoint: string; count: number; pct: number;
  avgMs: number; errors: number; errorPct: number; }
interface ApiUsageBreakdownProps { breakdown: BreakdownItem[];
  totalRequests: number; uniqueEndpoints: number; }

export function ApiUsageBreakdown({ breakdown, totalRequests, uniqueEndpoints }: ApiUsageBreakdownProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 API Usage Breakdown</h3>
        <span className="text-xs text-gray-400">{totalRequests.toLocaleString()} requests · {uniqueEndpoints} endpoints</span>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 text-left">Endpoint</th><th className="p-3">Count</th>
          <th className="p-3">%</th><th className="p-3">Avg</th><th className="p-3">Errors</th>
        </tr></thead>
        <tbody>
          {breakdown.map(b => (
            <tr key={b.endpoint} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3 font-mono text-xs">{b.endpoint}</td>
              <td className="p-3 text-center">{b.count.toLocaleString()}</td>
              <td className="p-3 text-center">{b.pct}%</td>
              <td className="p-3 text-center">{b.avgMs}ms</td>
              <td className="p-3 text-center">
                {b.errors > 0 ? <span className="text-red-500">{b.errorPct}%</span> : <span className="text-green-600">0%</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
