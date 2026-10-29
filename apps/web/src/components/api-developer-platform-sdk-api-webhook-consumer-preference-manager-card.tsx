"use client";

interface PrefInfo { consumer_id: string; max_retries: number; timeout_ms: number; content_type: string; signature_algorithm: string; batch_enabled: boolean; }
interface Props { preferences: PrefInfo[]; batchCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiWebhookConsumerPreferenceManagerCard({ preferences, batchCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚙️ Consumer Delivery Settings</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {preferences.length} configured</p>
        </div>
        <span className="text-[10px] text-gray-400">{batchCount} batch enabled</span>
      </div>
      {preferences.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No custom preferences</p>
      ) : (
        <div className="space-y-1.5">
          {preferences.slice(0, 5).map((p) => (
            <div key={p.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{p.consumer_id}</span>
              <span className="text-gray-400">{p.max_retries} retries · {p.timeout_ms}ms · {p.signature_algorithm}{p.batch_enabled ? " · batch" : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
