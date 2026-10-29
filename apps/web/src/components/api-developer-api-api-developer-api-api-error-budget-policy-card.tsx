"use client";

interface PolicyInfo { policy_id: string; endpoint: string; slo_pct: number; remaining_failures: number; allowed_failures: number; burn_rate: number; exhausted: boolean; }
interface Props { policies: PolicyInfo[]; exhaustedCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiErrorBudgetPolicyCard({ policies, exhaustedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Error Budget Policy</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {exhaustedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{exhaustedCount} exhausted</span>}
      </div>
      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No budget policies</p>
      ) : (
        <div className="space-y-2">
          {policies.map((p) => (
            <div key={p.policy_id} className={`rounded-lg p-2 ${p.exhausted ? "bg-red-50 dark:bg-red-900/20" : "bg-gray-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{p.endpoint}</span>
                <span className={p.exhausted ? "text-red-500 font-bold" : "text-green-600"}>{p.remaining_failures}/{p.allowed_failures} remaining</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>SLO: {p.slo_pct}%</span>
                <span>burn: {p.burn_rate}x</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
