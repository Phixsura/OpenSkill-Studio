"use client";

interface Entry { keyId: string; endpoint: string; method: string; allowed: boolean; }
interface Props { entries: Entry[]; keyId: string; consumerId: string; defaultAllow: boolean; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiKeyPermissionMatrixCard({ entries, keyId, consumerId, defaultAllow, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Permission Matrix</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · Key: {keyId} · Default: {defaultAllow ? "Allow" : "Deny"}</p>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No explicit permissions</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e, i) => (
            <div key={i} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <div className="flex items-center gap-1">
                <span className="font-bold text-blue-600">{e.method}</span>
                <code className="text-gray-600 dark:text-gray-400">{e.endpoint}</code>
              </div>
              <span className={e.allowed ? "text-green-500" : "text-red-500"}>{e.allowed ? "✓ Allow" : "✗ Deny"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
