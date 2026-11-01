"use client";

interface AdoptionInfo { consumer_id: string; primary_version: string; using_latest: boolean; multi_version: boolean; }
interface Props { adoptions: AdoptionInfo[]; versionDistribution: Record<string, number>; oldVersionCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiConsumerApiVersionAdoptionCard({ adoptions, versionDistribution, oldVersionCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Version Adoption</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {oldVersionCount > 0 && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-[10px] text-yellow-700">{oldVersionCount} on old versions</span>}
      </div>
      <div className="mb-3 flex gap-2">
        {Object.entries(versionDistribution).map(([v, c]) => (
          <span key={v} className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] text-blue-700 dark:bg-blue-900 dark:text-blue-200">{v}: {c.toLocaleString()}</span>
        ))}
      </div>
      {adoptions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No adoption data</p>
      ) : (
        <div className="space-y-1">
          {adoptions.slice(0, 5).map((a) => (
            <div key={a.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{a.consumer_id}</span>
              <span className={a.using_latest ? "text-green-600" : "text-yellow-600"}>{a.primary_version}{a.multi_version ? " (multi)" : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
