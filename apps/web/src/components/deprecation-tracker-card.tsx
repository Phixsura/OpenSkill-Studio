"use client";

interface DeprecationInfo {
  deprecation_id: string;
  resource: string;
  sunset_date: string;
  replacement: string;
  migration_progress: number;
  usage_count: number;
}

interface DeprecationTrackerCardProps {
  deprecations: DeprecationInfo[];
  appName: string;
}

export default function DeprecationTrackerCard({
  deprecations,
  appName,
}: DeprecationTrackerCardProps) {
  const unmigrated = deprecations.filter((d) => d.migration_progress < 100).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Deprecations</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unmigrated > 0 ? (
          <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
            {unmigrated} pending
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            All migrated
          </span>
        )}
      </div>

      {deprecations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No deprecations</p>
      ) : (
        <div className="space-y-2.5">
          {deprecations.map((d) => {
            const barColor =
              d.migration_progress >= 100
                ? "bg-green-500"
                : d.migration_progress >= 50
                  ? "bg-yellow-500"
                  : "bg-red-500";
            return (
              <div
                key={d.deprecation_id}
                className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-gray-800 dark:text-gray-200">
                    {d.resource}
                  </span>
                  <span className="text-[10px] text-gray-400">sunset {d.sunset_date}</span>
                </div>
                {d.replacement && (
                  <p className="mt-0.5 text-[11px] text-gray-400">→ {d.replacement}</p>
                )}
                <div className="mt-1.5 flex items-center gap-2">
                  <div className="h-1.5 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
                    <div
                      className={`h-1.5 rounded-full ${barColor}`}
                      style={{ width: `${Math.min(d.migration_progress, 100)}%` }}
                    />
                  </div>
                  <span className="text-[11px] text-gray-500">{d.migration_progress}%</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
