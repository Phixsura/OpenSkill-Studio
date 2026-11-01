"use client";

interface ApiUsageChartProps {
  totalCalls: number;
  quota: number;
  usagePct: number;
  topEndpoints: { endpoint: string; count: number }[];
}

export function ApiUsageChart({ totalCalls, quota, usagePct, topEndpoints }: ApiUsageChartProps) {
  const barColor = usagePct > 90 ? "bg-red-500" : usagePct > 70 ? "bg-yellow-500" : "bg-green-500";

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">API Usage</h3>
      <div className="mt-3">
        <div className="flex justify-between text-sm">
          <span>{totalCalls.toLocaleString()} / {quota.toLocaleString()} calls</span>
          <span className={usagePct > 90 ? "text-red-600" : ""}>{usagePct}%</span>
        </div>
        <div className="mt-1 h-3 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className={`h-full rounded-full ${barColor}`} style={{ width: `${Math.min(usagePct, 100)}%` }} />
        </div>
      </div>
      {topEndpoints.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-medium text-gray-500">Top Endpoints</p>
          <ul className="mt-1 space-y-1">
            {topEndpoints.map(e => (
              <li key={e.endpoint} className="flex justify-between text-xs">
                <code className="text-gray-600 dark:text-gray-400">{e.endpoint}</code>
                <span>{e.count}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
