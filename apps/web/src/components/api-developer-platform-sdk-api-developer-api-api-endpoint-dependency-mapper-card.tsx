"use client";

interface DepInfo { endpoint: string; dependency_count: number; dependent_count: number; is_critical: boolean; }
interface Props { endpoints: DepInfo[]; criticalCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiDeveloperApiApiEndpointDependencyMapperCard({ endpoints, criticalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🕸️ Endpoint Dependencies</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {criticalCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{criticalCount} critical</span>}
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No dependencies mapped</p>
      ) : (
        <div className="space-y-1">
          {endpoints.slice(0, 6).map((e) => (
            <div key={e.endpoint} className="flex items-center justify-between text-[11px]">
              <span className={`text-gray-700 dark:text-gray-300 ${e.is_critical ? "font-bold" : ""}`}>{e.endpoint}</span>
              <span className="text-gray-400">{e.dependency_count} deps · {e.dependent_count} dependents</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
