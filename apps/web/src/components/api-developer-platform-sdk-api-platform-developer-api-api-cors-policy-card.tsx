"use client";

interface PolicyInfo { policy_id: string; endpoint: string; origins: string[]; credentials: boolean; max_age_s: number; }
interface Props { policies: PolicyInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiCorsPolicyCard({ policies, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌍 CORS Policies</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {policies.length} policies</p>
      </div>
      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No CORS policies</p>
      ) : (
        <div className="space-y-2">
          {policies.map((p) => (
            <div key={p.policy_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="font-mono text-gray-700 dark:text-gray-300">{p.endpoint}</span>
                {p.credentials && <span className="rounded bg-amber-100 px-1 text-[9px] text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">credentials</span>}
              </div>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {p.origins.map((o) => (
                  <span key={o} className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800 dark:text-gray-400">{o}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
