"use client";

interface PolicyInfo { consumer_id: string; max_replays: number; window_hours: number; auto_replay: boolean; delay_s: number; }
interface Props { policies: PolicyInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventReplayPolicyCard({ policies, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔁 Replay Policies</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {policies.length} policies</p>
      </div>
      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No replay policies</p>
      ) : (
        <div className="space-y-1">
          {policies.map((p) => (
            <div key={p.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{p.consumer_id}</span>
              <span className="text-gray-400">{p.max_replays}× · {p.window_hours}h · {p.delay_s}s delay{p.auto_replay ? " · auto" : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
