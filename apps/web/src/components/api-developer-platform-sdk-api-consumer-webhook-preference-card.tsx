"use client";

interface PrefInfo { consumer_id: string; preferred_format: string; compression: string; batch_enabled: boolean; }
interface Props { preferences: PrefInfo[]; formatDistribution: Record<string, number>; batchCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiConsumerWebhookPreferenceCard({ preferences, formatDistribution, batchCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚙️ Webhook Preferences</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {preferences.length} consumers</p>
        </div>
        <span className="text-[10px] text-gray-400">{batchCount} batch enabled</span>
      </div>
      <div className="mb-3 flex gap-2">
        {Object.entries(formatDistribution).map(([fmt, count]) => (
          <span key={fmt} className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] text-blue-700 dark:bg-blue-900 dark:text-blue-200">{fmt}: {count}</span>
        ))}
      </div>
      {preferences.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No preferences set</p>
      ) : (
        <div className="space-y-1">
          {preferences.slice(0, 5).map((p) => (
            <div key={p.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{p.consumer_id}</span>
              <span className="text-gray-400">{p.preferred_format}{p.compression !== "none" ? ` · ${p.compression}` : ""}{p.batch_enabled ? " · batch" : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
