"use client";

interface PolicyInfo { policy_id: string; consumer_id: string; strategy: string; max_retries: number; base_delay_s: number; }
interface Props { policies: PolicyInfo[]; appName: string; }

const stratEmoji: Record<string, string> = { fixed: "➡️", exponential: "📈", linear: "📊" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookRetryPolicyCard({ policies, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔁 Retry Policies</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {policies.length} policies</p>
      </div>
      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No retry policies</p>
      ) : (
        <div className="space-y-1.5">
          {policies.map((p) => (
            <div key={p.policy_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{stratEmoji[p.strategy] ?? "•"}</span>
                <span className="text-gray-700 dark:text-gray-300">{p.consumer_id}</span>
              </div>
              <span className="text-gray-400">{p.strategy} · {p.max_retries}× · {p.base_delay_s}s</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
