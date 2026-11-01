"use client";

interface KeyInfo { key_id: string; consumer_id: string; days_until_expiry: number; urgency: string; expired: boolean; }
interface Props { keys: KeyInfo[]; expiringCount: number; expiredCount: number; appName: string; }

const uColor: Record<string, string> = { expired: "bg-red-100 text-red-700", critical: "bg-orange-100 text-orange-700", warning: "bg-yellow-100 text-yellow-700", ok: "bg-green-100 text-green-700" };

export default function APIDeveloperPlatformSDKApiPlatformApiDeveloperApiKeyExpiryMonitorCard({ keys, expiringCount, expiredCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏰ Key Expiry Monitor</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-1">
          {expiredCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{expiredCount} expired</span>}
          {expiringCount > 0 && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-[10px] text-yellow-700">{expiringCount} expiring</span>}
        </div>
      </div>
      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No key expiry data</p>
      ) : (
        <div className="space-y-1">
          {keys.slice(0, 6).map((k) => (
            <div key={k.key_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{k.consumer_id} / {k.key_id}</span>
              <span className={`rounded px-1 py-0.5 text-[9px] ${uColor[k.urgency] ?? ""}`}>{k.expired ? "EXPIRED" : `${k.days_until_expiry}d`}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
