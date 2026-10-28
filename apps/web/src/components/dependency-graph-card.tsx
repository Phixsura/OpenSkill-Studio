"use client";

interface ServiceNodeInfo {
  service_id: string;
  name: string;
  depends_on: string[];
  dependent_count: number;
}

interface DependencyGraphCardProps {
  services: ServiceNodeInfo[];
  hasCircular: boolean;
  appName: string;
}

export default function DependencyGraphCard({
  services,
  hasCircular,
  appName,
}: DependencyGraphCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Service Dependencies
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          {hasCircular && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              ⚠ Circular
            </span>
          )}
          <span className="text-xs text-gray-400">{services.length} services</span>
        </div>
      </div>

      {services.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No services registered</p>
      ) : (
        <div className="space-y-2">
          {services.map((s) => (
            <div
              key={s.service_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  {s.name}
                </span>
                {s.dependent_count > 0 && (
                  <span className="text-[11px] text-gray-400">{s.dependent_count} dependents</span>
                )}
              </div>
              {s.depends_on.length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1">
                  {s.depends_on.map((dep) => (
                    <span
                      key={dep}
                      className="inline-flex items-center gap-0.5 rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                    >
                      ← {dep}
                    </span>
                  ))}
                </div>
              )}
              {s.depends_on.length === 0 && (
                <p className="mt-0.5 text-[10px] text-gray-400">No dependencies (root)</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
