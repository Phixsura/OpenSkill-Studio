"use client";

interface PolicyInfo { consumer_id: string; mode: string; regions: string[]; action: string; }
interface Props { policies: PolicyInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGeoRestrictionCard({ policies, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌍 Geo Restrictions</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {policies.length} policies</p>
      </div>
      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No geo restrictions</p>
      ) : (
        <div className="space-y-1.5">
          {policies.map((p) => (
            <div key={p.consumer_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{p.consumer_id}</span>
                <span className={p.mode === "allowlist" ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}>{p.mode}</span>
              </div>
              <div className="flex flex-wrap gap-1 mt-0.5">
                {p.regions.map((r) => <span key={r} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{r}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
