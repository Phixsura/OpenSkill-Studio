"use client";

interface Perm { id: string; endpoint: string; method: string; allowed: boolean; rateLimit: number | null; }
interface Props { permissions: Perm[]; consumerId: string; defaultAllowed: boolean; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiEndpointPermissionCard({ permissions, consumerId, defaultAllowed, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Endpoint Permissions</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · Default: {defaultAllowed ? "Allow" : "Deny"}</p>
      </div>
      {permissions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No explicit permissions</p>
      ) : (
        <div className="space-y-1">
          {permissions.map((p) => (
            <div key={p.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <div className="flex items-center gap-1">
                <span className="font-bold text-blue-600">{p.method}</span>
                <code className="text-gray-600 dark:text-gray-400">{p.endpoint}</code>
              </div>
              <div className="flex gap-1">
                <span className={p.allowed ? "text-green-500" : "text-red-500"}>{p.allowed ? "✓" : "✗"}</span>
                {p.rateLimit && <span className="text-gray-400">{p.rateLimit}/s</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
