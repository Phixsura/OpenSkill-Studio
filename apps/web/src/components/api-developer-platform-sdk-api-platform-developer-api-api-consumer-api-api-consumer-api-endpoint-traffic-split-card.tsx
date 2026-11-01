"use client";

interface Target { id: string; version: string; weight: number; }
interface Props { endpointPath: string; targets: Target[]; sticky: boolean; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointTrafficSplitCard({ endpointPath, targets, sticky, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔀 Traffic Split</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — <code>{endpointPath}</code> · {sticky ? "Sticky" : "Random"}</p>
      </div>
      {targets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No targets</p>
      ) : (
        <div className="space-y-1">
          {targets.map((t) => (
            <div key={t.id} className="flex items-center gap-2 text-[11px]">
              <div className="h-2 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-blue-500" style={{ width: `${t.weight}%` }} />
              </div>
              <span className="w-10 text-right font-bold text-gray-700 dark:text-gray-300">{t.weight}%</span>
              <span className="text-gray-500">{t.version}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
