"use client";

interface UsageInfo { consumer_id: string; feature_count: number; total_usage: number; top_feature: string; }
interface Props { consumers: UsageInfo[]; featurePopularity: Record<string, number>; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformApiConsumerFeatureUsageCard({ consumers, featurePopularity, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Feature Usage</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumers.length} consumers</p>
      </div>
      <div className="mb-3 flex flex-wrap gap-1">
        {Object.entries(featurePopularity).slice(0, 5).map(([f, c]) => (
          <span key={f} className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] text-blue-700 dark:bg-blue-900 dark:text-blue-200">{f}: {c} users</span>
        ))}
      </div>
      {consumers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage data</p>
      ) : (
        <div className="space-y-1">
          {consumers.slice(0, 5).map((c) => (
            <div key={c.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
              <span className="text-gray-400">{c.feature_count} features · top: {c.top_feature}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
