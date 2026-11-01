"use client";

interface ConfigInfo { consumer_id: string; target_rps: number; burst_tolerance: number; }
interface Props { configs: ConfigInfo[]; shapingRate: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRateShaperCard({ configs, shapingRate, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📉 Rate Shaper</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{shapingRate}% shaped</span>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate shaping configs</p>
      ) : (
        <div className="space-y-1">
          {configs.map((c) => (
            <div key={c.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
              <span className="text-gray-400">{c.target_rps} rps · {c.burst_tolerance}x burst</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
