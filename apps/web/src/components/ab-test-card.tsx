"use client";

interface VariantResult {
  name: string;
  impressions: number;
  conversions: number;
  rate: number;
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

export default function ABTestCard({ experiments, appName }: ABTestCardProps) {
  const active = experiments.filter((e) => e.active).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧪 A/B Tests</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {active} active / {experiments.length} total
        </span>
      </div>

      {experiments.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No experiments</p>
      ) : (
        <div className="space-y-3">
          {experiments.map((exp) => {
            const winner = [...exp.variants].sort((a, b) => b.rate - a.rate)[0];
            return (
              <div
                key={exp.experiment_id}
                className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                    {exp.name}
                  </span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                      exp.active
                        ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                        : "bg-gray-100 text-gray-500 dark:bg-gray-800"
                    }`}
                  >
                    {exp.active ? "active" : "ended"}
                  </span>
                </div>
                <div className="mt-1.5 space-y-0.5">
                  {exp.variants.map((v) => (
                    <div key={v.name} className="flex items-center justify-between text-[11px]">
                      <span
                        className={`text-gray-600 dark:text-gray-400 ${v.name === winner?.name ? "font-medium" : ""}`}
                      >
                        {v.name} {v.name === winner?.name && winner.rate > 0 ? "👑" : ""}
                      </span>
                      <span className="text-gray-400">
                        {v.rate}% ({v.conversions}/{v.impressions})
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
