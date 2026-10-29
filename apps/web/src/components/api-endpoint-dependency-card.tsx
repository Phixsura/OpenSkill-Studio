"use client";

interface DepInfo { method: string; path: string; dependency_count: number; }
interface Props { endpoints: DepInfo[]; appName: string; }

export default function APIEndpointDependencyCard({ endpoints, appName }: Props) {
  const withDeps = endpoints.filter((e) => e.dependency_count > 0).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔗 Endpoint Deps</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{withDeps}/{endpoints.length} with deps</span>
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoint dependencies</p>
      ) : (
        <div className="space-y-1">
          {endpoints.map((e) => (
            <div key={`${e.method}-${e.path}`} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800">{e.method}</span>
                <span className="font-mono text-gray-700 dark:text-gray-300">{e.path}</span>
              </div>
              <span className="text-gray-400">{e.dependency_count} deps</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
