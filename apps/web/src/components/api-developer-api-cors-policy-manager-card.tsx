"use client";

interface PolicyInfo { policy_id: string; allowed_origins: string[]; allowed_methods: string[]; allow_credentials: boolean; max_age_seconds: number; }
interface Props { policies: PolicyInfo[]; appName: string; }

export default function APIDeveloperAPICORSPolicyManagerCard({ policies, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌐 CORS Policies</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {policies.length} policies</p>
      </div>
      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No CORS policies</p>
      ) : (
        <div className="space-y-2">
          {policies.map((p) => (
            <div key={p.policy_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{p.policy_id}</span>
                {p.allow_credentials && <span className="rounded bg-yellow-100 px-1 py-0.5 text-[9px] text-yellow-700">credentials</span>}
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">Origins: {p.allowed_origins.join(", ")} · Methods: {p.allowed_methods.join(", ")}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
