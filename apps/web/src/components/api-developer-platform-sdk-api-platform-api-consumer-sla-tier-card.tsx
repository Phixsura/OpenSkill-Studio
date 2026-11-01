"use client";

interface TierInfo { consumer_id: string; tier: string; uptime_target: number; actual_uptime: number; latency_target_ms: number; actual_latency_ms: number; meeting_sla: boolean; }
interface Props { consumers: TierInfo[]; tierCounts: Record<string, number>; breachingCount: number; appName: string; }

const tBadge: Record<string, string> = { platinum: "bg-purple-100 text-purple-700", gold: "bg-yellow-100 text-yellow-700", silver: "bg-gray-200 text-gray-700", bronze: "bg-orange-100 text-orange-700" };

export default function APIDeveloperPlatformSDKApiPlatformApiConsumerSLATierCard({ consumers, tierCounts, breachingCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏅 SLA Tiers</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {breachingCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{breachingCount} breaching</span>}
      </div>
      <div className="mb-3 flex gap-2">
        {Object.entries(tierCounts).map(([tier, count]) => (
          <span key={tier} className={`rounded px-1.5 py-0.5 text-[10px] ${tBadge[tier] ?? ""}`}>{tier}: {count}</span>
        ))}
      </div>
      {consumers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SLA data</p>
      ) : (
        <div className="space-y-1">
          {consumers.slice(0, 5).map((c) => (
            <div key={c.consumer_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`rounded px-1 py-0.5 text-[9px] ${tBadge[c.tier] ?? ""}`}>{c.tier}</span>
                <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
              </div>
              <span className={c.meeting_sla ? "text-green-600" : "text-red-500 font-bold"}>{c.meeting_sla ? "✓" : "✗"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
