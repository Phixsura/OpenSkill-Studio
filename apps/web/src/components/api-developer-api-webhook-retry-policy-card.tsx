"use client";

interface PolicyInfo { policy_id: string; max_retries: number; base_delay_seconds: number; max_delay_seconds: number; strategy: string; schedule: number[]; }
interface Props { policies: PolicyInfo[]; appName: string; }

export default function APIDeveloperAPIWebhookRetryPolicyCard({ policies, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔁 Retry Policies</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {policies.length} policies</p>
      </div>
      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No retry policies</p>
      ) : (
        <div className="space-y-2">
          {policies.map((p) => (
            <div key={p.policy_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{p.policy_id}</span>
                <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[9px] text-blue-700">{p.strategy}</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">{p.max_retries} retries · delays: {p.schedule.map(s => `${s}s`).join(" → ")}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
