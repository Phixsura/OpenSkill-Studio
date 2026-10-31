"use client";

interface Owner { endpoint: string; team: string; ownerEmail: string; slaTier: string; }
interface Props { owners: Owner[]; byTeam: Record<string, number>; unownedCount: number; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiEndpointOwnershipRegistryCard({ owners, byTeam, unownedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👤 Endpoint Ownership</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {owners.length} owned{unownedCount > 0 ? ` · ${unownedCount} unowned` : ""}</p>
      </div>
      {Object.keys(byTeam).length > 0 && (
        <div className="mb-3 flex flex-wrap gap-1">
          {Object.entries(byTeam).map(([team, count]) => (
            <span key={team} className="rounded bg-blue-100 px-1.5 py-0.5 text-[9px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{team}: {count}</span>
          ))}
        </div>
      )}
      {owners.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No ownership data</p>
      ) : (
        <div className="space-y-0.5">
          {owners.slice(0, 8).map((o) => (
            <div key={o.endpoint} className="flex items-center justify-between text-[10px]">
              <code className="text-gray-600 dark:text-gray-400">{o.endpoint}</code>
              <span className="text-gray-500">{o.team}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
