"use client";

interface RuleInfo { rule_id: string; event_pattern: string; priority: number; }
interface Props { consumerId: string; rules: RuleInfo[]; appName: string; }

const prioLabel: Record<number, string> = { 1: "🔴 Critical", 2: "🟠 High", 3: "🟡 Medium", 4: "🔵 Low", 5: "⚪ Lowest" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventPriorityCard({ consumerId, rules, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏷️ Event Priority</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {rules.length} rules</p>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No priority rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{r.event_pattern}</span>
              <span className="text-gray-400">{prioLabel[r.priority] ?? `P${r.priority}`}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
