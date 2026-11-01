"use client";

interface PolicyInfo { policy_id: string; endpoint: string; add_count: number; remove_count: number; }
interface Props { policies: PolicyInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiResponseHeaderPolicyCard({ policies, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📨 Response Headers</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {policies.length} policies</p>
      </div>
      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No header policies</p>
      ) : (
        <div className="space-y-1">
          {policies.map((p) => (
            <div key={p.policy_id} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{p.endpoint}</span>
              <span className="text-gray-400">+{p.add_count} −{p.remove_count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
