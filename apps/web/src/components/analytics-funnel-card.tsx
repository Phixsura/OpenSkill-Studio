"use client";

interface StepMetric {
  step_id: string;
  name: string;
  entered: number;
  conversion_pct: number;
  drop_off_pct: number;
}

interface AnalyticsFunnelCardProps {
  funnelName: string;
  steps: StepMetric[];
  overallConversion: number;
  appName: string;
}

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function AnalyticsFunnelCard({
  funnelName,
  steps,
  overallConversion,
  appName,
}: AnalyticsFunnelCardProps) {
  const maxEntered = Math.max(...steps.map((s) => s.entered), 1);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">{funnelName}</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span
          className={`text-sm font-bold ${overallConversion >= 10 ? "text-green-600 dark:text-green-400" : "text-yellow-600 dark:text-yellow-400"}`}
        >
          {overallConversion}% conversion
        </span>
      </div>

      <div className="space-y-2">
        {steps.map((s, i) => {
          const barWidth = maxEntered > 0 ? (s.entered / maxEntered) * 100 : 0;
          return (
            <div key={s.step_id}>
              <div className="mb-0.5 flex items-center justify-between text-xs">
                <span className="text-gray-700 dark:text-gray-300">{s.name}</span>
                <span className="text-gray-500">{formatNum(s.entered)} users</span>
              </div>
              <div className="h-6 rounded bg-gray-100 dark:bg-gray-800">
                <div
                  className="flex h-6 items-center rounded bg-blue-500/20 px-2"
                  style={{ width: `${Math.max(barWidth, 2)}%` }}
                >
                  <span className="text-[10px] font-medium text-blue-700 dark:text-blue-400">
                    {i === 0 ? "100%" : `${s.conversion_pct}%`}
                  </span>
                </div>
              </div>
              {i > 0 && s.drop_off_pct > 0 && (
                <p className="mt-0.5 text-right text-[10px] text-red-400">
                  −{s.drop_off_pct}% drop-off
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
