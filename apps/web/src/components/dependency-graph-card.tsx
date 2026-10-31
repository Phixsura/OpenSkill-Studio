"use client";

interface ServiceNodeInfo {
  service_id: string;
  name: string;
  version: string;
  depends_on: string[];
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
  const totalDeps = services.reduce((sum, s) => sum + s.depends_on.length, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔗 Dependency Graph
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{services.length} services</span>
          {hasCircular && (
            <p className="text-[10px] font-medium text-red-600 dark:text-red-400">
              ⚠ Circular detected
            </p>
          )}
        </div>
      </div>

      <div className="mb-3 flex gap-3 text-center">
        <div className="flex-1 rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{services.length}</p>
          <p className="text-[10px] text-gray-500">Services</p>
        </div>
        <div className="flex-1 rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{totalDeps}</p>
          <p className="text-[10px] text-gray-500">Edges</p>
        </div>
      </div>

      {services.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No services registered</p>
      ) : (
        <div className="space-y-1.5">
          {services.map((s) => (
            <div
              key={s.service_id}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
            >
              <div>
                <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  {s.name}
                </span>
                {s.version && <span className="ml-1 text-[10px] text-gray-400">{s.version}</span>}
              </div>
              <span className="text-[11px] text-gray-400">
                {s.depends_on.length === 0 ? "no deps" : `${s.depends_on.length} deps`}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
