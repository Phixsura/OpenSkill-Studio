"use client";

interface OwnerInfo { endpoint: string; owner_team: string; oncall_contact: string; sla_tier: string; }
interface Props { ownership: OwnerInfo[]; teamDistribution: Record<string, number>; unownedCount: number; appName: string; }

const slaBadge: Record<string, string> = { critical: "bg-red-100 text-red-700", standard: "bg-blue-100 text-blue-700", best_effort: "bg-gray-100 text-gray-600" };

export default function APIDeveloperPlatformSDKApiPlatformApiDeveloperApiEndpointOwnershipCard({ ownership, teamDistribution, unownedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👥 Endpoint Ownership</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unownedCount > 0 && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-[10px] text-yellow-700">{unownedCount} unowned</span>}
      </div>
      <div className="mb-3 flex flex-wrap gap-1">
        {Object.entries(teamDistribution).map(([team, count]) => (
          <span key={team} className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] text-blue-700 dark:bg-blue-900 dark:text-blue-200">{team}: {count}</span>
        ))}
      </div>
      {ownership.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No ownership data</p>
      ) : (
        <div className="space-y-1">
          {ownership.slice(0, 6).map((o) => (
            <div key={o.endpoint} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{o.endpoint}</span>
              <div className="flex gap-1.5">
                <span className="text-gray-400">{o.owner_team}</span>
                <span className={`rounded px-1 py-0.5 text-[8px] ${slaBadge[o.sla_tier] ?? ""}`}>{o.sla_tier}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
