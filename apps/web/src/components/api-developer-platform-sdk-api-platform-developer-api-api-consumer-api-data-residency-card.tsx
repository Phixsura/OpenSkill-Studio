"use client";

interface ConfigInfo { consumer_id: string; primary_region: string; allowed_regions: string[]; compliance_frameworks: string[]; }
interface Props { configs: ConfigInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiDataResidencyCard({ configs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌍 Data Residency</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {configs.length} consumers</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No residency configs</p>
      ) : (
        <div className="space-y-2">
          {configs.map((c) => (
            <div key={c.consumer_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
                <span className="font-medium text-blue-600 dark:text-blue-400">{c.primary_region}</span>
              </div>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {c.compliance_frameworks.map((f) => <span key={f} className="rounded bg-purple-100 px-1 text-[9px] text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">{f}</span>)}
                {c.allowed_regions.map((r) => <span key={r} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{r}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
