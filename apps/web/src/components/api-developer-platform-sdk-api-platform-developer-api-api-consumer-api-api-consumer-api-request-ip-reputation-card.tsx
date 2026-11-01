"use client";

interface RepInfo { ip_address: string; score: number; tier: string; total_requests: number; suspicious_events: number; }
interface Props { reputations: RepInfo[]; suspiciousCount: number; appName: string; }

const tierColor: Record<string, string> = { trusted: "text-green-600 dark:text-green-400", neutral: "text-gray-400", suspicious: "text-orange-600 dark:text-orange-400", blocked: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIpReputationCard({ reputations, suspiciousCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🛡️ IP Reputation</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {suspiciousCount > 0 && <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] font-medium text-orange-700 dark:bg-orange-900/30 dark:text-orange-400">⚠️ {suspiciousCount} suspicious</span>}
      </div>
      {reputations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No IP data</p>
      ) : (
        <div className="space-y-1">
          {reputations.map((r) => (
            <div key={r.ip_address} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{r.ip_address}</span>
              <span className={tierColor[r.tier]}>{r.score} · {r.tier}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
