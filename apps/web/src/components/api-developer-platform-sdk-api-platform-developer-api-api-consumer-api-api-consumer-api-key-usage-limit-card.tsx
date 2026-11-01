"use client";

interface LimitInfo { key_id: string; daily_limit: number; daily_used: number; monthly_limit: number; monthly_used: number; }
interface Props { limits: LimitInfo[]; nearLimitCount: number; appName: string; }

const barColor = (used: number, limit: number) => { const pct = limit > 0 ? used / limit * 100 : 0; return pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-yellow-500" : "bg-green-500"; };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyUsageLimitCard({ limits, nearLimitCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Key Usage Limits</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {nearLimitCount > 0 && <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">⚠️ {nearLimitCount} near limit</span>}
      </div>
      {limits.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage limits</p>
      ) : (
        <div className="space-y-1.5">
          {limits.map((l) => (
            <div key={l.key_id} className="text-[11px]">
              <div className="flex justify-between"><span className="font-mono text-gray-700 dark:text-gray-300">{l.key_id}</span><span className="text-gray-400">{l.daily_used}/{l.daily_limit}/day · {l.monthly_used.toLocaleString()}/{l.monthly_limit.toLocaleString()}/mo</span></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
