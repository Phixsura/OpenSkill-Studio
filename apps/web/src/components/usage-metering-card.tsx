"use client";

interface MetricSummary {
  metric: string;
  total: number;
  periods: number;
}

interface UsageMeteringCardProps {
  metrics: MetricSummary[];
  appName: string;
}

export default function UsageMeteringCard({ metrics, appName }: UsageMeteringCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📈 Usage Metering
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{metrics.length} metrics</span>
      </div>

      {metrics.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage data</p>
      ) : (
        <div className="space-y-2">
          {metrics.map((m) => (
            <div
              key={m.metric}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                {m.metric}
              </span>
              <div className="text-right">
                <span className="text-sm font-bold text-gray-900 dark:text-gray-100">
                  {m.total.toLocaleString()}
                </span>
                <p className="text-[10px] text-gray-400">{m.periods} periods</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
