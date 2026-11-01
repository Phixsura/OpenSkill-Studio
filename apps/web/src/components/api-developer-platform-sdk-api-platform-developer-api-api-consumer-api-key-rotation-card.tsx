"use client";

interface VersionInfo { version: number; is_current: boolean; revoked: boolean; grace_remaining_min: number; }
interface Props { consumerId: string; versions: VersionInfo[]; currentVersion: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiKeyRotationCard({ consumerId, versions, currentVersion, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Key Rotation</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className="text-[10px] text-gray-400">v{currentVersion} active</span>
      </div>
      {versions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No keys issued</p>
      ) : (
        <div className="space-y-1">
          {versions.map((v) => (
            <div key={v.version} className="flex items-center justify-between text-[11px]">
              <span className={`${v.is_current ? "font-medium text-green-600 dark:text-green-400" : v.revoked ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-300"}`}>v{v.version}{v.is_current ? " (current)" : ""}</span>
              {!v.revoked && !v.is_current && v.grace_remaining_min > 0 && <span className="text-[10px] text-amber-500">{v.grace_remaining_min}m grace</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
