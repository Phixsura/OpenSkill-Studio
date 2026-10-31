"use client";

interface ConfigInfo { consumer_id: string; wrap_key: string; include_meta: boolean; include_pagination: boolean; }
interface Props { configs: ConfigInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseEnvelopeCard({ configs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 Response Envelope</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {configs.length} configs</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No envelope configs</p>
      ) : (
        <div className="space-y-1">
          {configs.map((c) => (
            <div key={c.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
              <div className="flex gap-1">
                <span className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{c.wrap_key}</span>
                {c.include_meta && <span className="text-[9px] text-blue-600 dark:text-blue-400">+meta</span>}
                {c.include_pagination && <span className="text-[9px] text-green-600 dark:text-green-400">+page</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
