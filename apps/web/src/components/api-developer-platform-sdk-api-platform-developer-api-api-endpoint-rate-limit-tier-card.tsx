"use client";

interface TierInfo { tier: string; rpm: number; rph: number; burst: number; }
interface EndpointInfo { endpoint: string; method: string; tiers: TierInfo[]; }
interface Props { endpoints: EndpointInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointRateLimitTierCard({ endpoints, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏷️ Rate Limit Tiers</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {endpoints.length} endpoints</p>
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tier configs</p>
      ) : (
        <div className="space-y-2">
          {endpoints.map((e) => (
            <div key={`${e.method}-${e.endpoint}`} className="text-[11px]">
              <div className="font-medium text-gray-700 dark:text-gray-300">{e.method} {e.endpoint}</div>
              <div className="mt-0.5 flex gap-2">
                {e.tiers.map((t) => (
                  <span key={t.tier} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{t.tier}: {t.rpm}/min</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
