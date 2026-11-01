"use client";

interface ConfigInfo { endpoint: string; method: string; shadow_version: string; active: boolean; }
interface Props { configs: ConfigInfo[]; matchRate: number; mismatchCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestShadowModeCard({ configs, matchRate, mismatchCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👻 Shadow Mode</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <div className={`text-sm font-bold ${matchRate >= 95 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>{matchRate}% match</div>
          {mismatchCount > 0 && <div className="text-[10px] text-red-500">{mismatchCount} mismatches</div>}
        </div>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No shadow configs</p>
      ) : (
        <div className="space-y-1">
          {configs.map((c) => (
            <div key={`${c.method}-${c.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.method} {c.endpoint}</span>
              <span className={c.active ? "text-purple-600 dark:text-purple-400" : "text-gray-400"}>→ {c.shadow_version}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
