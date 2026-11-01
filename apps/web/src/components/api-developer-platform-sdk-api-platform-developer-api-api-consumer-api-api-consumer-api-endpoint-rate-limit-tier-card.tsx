"use client";

interface Tier { id: string; name: string; rps: number; rpm: number; rph: number; burst: number; }
interface Props { tiers: Tier[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointRateLimitTierCard({ tiers, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏱️ Rate Limit Tiers</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {tiers.length} tiers</p>
      </div>
      {tiers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate limit tiers</p>
      ) : (
        <div className="space-y-2">
          {tiers.map((t) => (
            <div key={t.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="text-[11px] font-medium text-gray-700 dark:text-gray-300">{t.name}</div>
              <div className="mt-0.5 grid grid-cols-4 gap-1 text-[10px] text-gray-400">
                <span>{t.rps}/s</span>
                <span>{t.rpm}/m</span>
                <span>{t.rph.toLocaleString()}/h</span>
                {t.burst > 0 && <span className="text-blue-500">+{t.burst} burst</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
