"use client";

interface Key { id: string; status: string; daysRemaining: number; expiresAt: string; }
interface Props { keys: Key[]; maxLifetimeDays: number; warnBeforeDays: number; consumerId: string; appName: string; }

const statusColors: Record<string, string> = {
  active: "text-green-500", warning: "text-amber-500", expired: "text-red-500", disabled: "text-gray-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyExpirationPolicyCard({ keys, maxLifetimeDays, warnBeforeDays, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏰ Key Expiration Policy</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · Max: {maxLifetimeDays}d · Warn: {warnBeforeDays}d</p>
      </div>
      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No keys tracked</p>
      ) : (
        <div className="space-y-1">
          {keys.map((k) => (
            <div key={k.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800">
              <code className="text-gray-700 dark:text-gray-300">{k.id}</code>
              <div className="flex gap-2">
                <span className="text-gray-400">{k.daysRemaining}d left</span>
                <span className={`font-medium ${statusColors[k.status] ?? ""}`}>{k.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
