"use client";

interface ExemptionInfo { exemption_id: string; consumer_id: string; reason: string; multiplier: number; active: boolean; hours_remaining: number; }
interface Props { exemptions: ExemptionInfo[]; activeCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRateLimitExemptionCard({ exemptions, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Rate Exemptions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {activeCount > 0 && <span className="rounded-full bg-green-100 px-2 py-0.5 text-[10px] font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">{activeCount} active</span>}
      </div>
      {exemptions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No exemptions</p>
      ) : (
        <div className="space-y-1">
          {exemptions.map((e) => (
            <div key={e.exemption_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{e.consumer_id} — {e.reason}</span>
              <span className={e.active ? "text-green-600 dark:text-green-400" : "text-gray-400"}>{e.multiplier}× · {e.hours_remaining > 0 ? `${e.hours_remaining}h` : "∞"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
