"use client";

interface PolicyInfo { policy_id: string; name: string; rule_count: number; consumer_count: number; enforcement: string; }
interface Props { policies: PolicyInfo[]; activeCount: number; appName: string; }

const eBadge: Record<string, string> = { enforce: "bg-green-100 text-green-700", monitor: "bg-blue-100 text-blue-700", disabled: "bg-gray-100 text-gray-500" };

export default function APIDeveloperPlatformSDKApiPlatformApiApiRateLimitPolicyEngineCard({ policies, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚙️ Rate Limit Policies</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount} active</p>
      </div>
      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No policies</p>
      ) : (
        <div className="space-y-2">
          {policies.map((p) => (
            <div key={p.policy_id} className="rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{p.name}</span>
                <span className={`rounded px-1 py-0.5 text-[9px] ${eBadge[p.enforcement] ?? ""}`}>{p.enforcement}</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">{p.rule_count} rules · {p.consumer_count} consumers</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
