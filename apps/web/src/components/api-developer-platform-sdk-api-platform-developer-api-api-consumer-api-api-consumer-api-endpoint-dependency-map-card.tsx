"use client";

interface Dep { from: string; to: string; type: string; critical: boolean; }
interface Props { dependencies: Dep[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDependencyMapCard({ dependencies, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗺️ Dependency Map</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {dependencies.length} dependencies</p>
      </div>
      {dependencies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No dependencies</p>
      ) : (
        <div className="space-y-1">
          {dependencies.map((d, i) => (
            <div key={i} className="flex items-center gap-1 rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <code className="text-gray-600 dark:text-gray-400">{d.from}</code>
              <span className="text-gray-400">→</span>
              <code className="text-blue-600 dark:text-blue-400">{d.to}</code>
              <span className="rounded bg-gray-200 px-1 py-0.5 text-[8px] text-gray-500 dark:bg-gray-700">{d.type}</span>
              {d.critical && <span className="text-red-500">⚠</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
