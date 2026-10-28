"use client";

interface VariantResult {
  name: string;
  exposures: number;
  conversions: number;
  conversion_rate: number;
}

interface ExperimentInfo {
  experiment_id: string;
  name: string;
  active: boolean;
  variants: VariantResult[];
}

interface ABTestCardProps {
  experiments: ExperimentInfo[];
  appName: string;
}

function ConversionBar({ rate, isWinner }: { rate: number; isWinner: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          className={`h-1.5 rounded-full ${isWinner ? "bg-green-500" : "bg-blue-500"}`}
          style={{ width: `${Math.min(rate, 100)}%` }}
        />
      </div>
      <span
        className={`text-xs font-medium ${isWinner ? "text-green-600 dark:text-green-400" : "text-gray-600 dark:text-gray-400"}`}
      >
        {rate.toFixed(1)}%
      </span>
    </div>
  );
}

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function ABTestCard({ experiments, appName }: ABTestCardProps) {
  const activeCount = experiments.filter((e) => e.active).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">A/B Tests</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{activeCount} active</span>
      </div>

      {experiments.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No experiments</p>
      ) : (
        <div className="space-y-4">
          {experiments.map((exp) => {
            const maxRate = Math.max(...exp.variants.map((v) => v.conversion_rate));
            return (
              <div
                key={exp.experiment_id}
                className="rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800"
              >
                <div className="mb-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                      {exp.name}
                    </span>
                    <span
                      className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                        exp.active
                          ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                          : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                      }`}
                    >
                      {exp.active ? "Running" : "Stopped"}
                    </span>
                  </div>
                </div>
                <div className="space-y-1.5">
                  {exp.variants.map((v) => (
                    <div key={v.name} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="w-20 text-xs text-gray-700 dark:text-gray-300">
                          {v.name}
                        </span>
                        <ConversionBar
                          rate={v.conversion_rate}
                          isWinner={v.conversion_rate === maxRate && maxRate > 0}
                        />
                      </div>
                      <span className="text-[11px] text-gray-400">
                        {formatNum(v.conversions)}/{formatNum(v.exposures)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
