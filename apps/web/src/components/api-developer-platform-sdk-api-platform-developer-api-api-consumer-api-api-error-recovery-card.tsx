"use client";

interface RuleInfo { rule_id: string; error_pattern: string; action: string; }
interface Props { rules: RuleInfo[]; recoveryRate: number; totalRecoveries: number; appName: string; }

const actionIcon: Record<string, string> = { retry: "🔄", fallback: "↩️", circuit_break: "⚡", escalate: "📢", ignore: "🚫" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorRecoveryCard({ rules, recoveryRate, totalRecoveries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔧 Error Recovery</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalRecoveries} recoveries</p>
        </div>
        <span className={`text-sm font-bold ${recoveryRate >= 80 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>{recoveryRate}%</span>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No recovery rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{r.error_pattern}</span>
              <span className="text-gray-400">{actionIcon[r.action] ?? "•"} {r.action}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
