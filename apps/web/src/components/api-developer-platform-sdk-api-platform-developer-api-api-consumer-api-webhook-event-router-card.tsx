"use client";

interface RuleInfo { rule_id: string; event_pattern: string; target_url: string; priority: number; }
interface ConfigInfo { consumer_id: string; rules: RuleInfo[]; default_url: string; }
interface Props { configs: ConfigInfo[]; totalRules: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventRouterCard({ configs, totalRules, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔀 Event Router</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {configs.length} consumers · {totalRules} rules</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No routing configs</p>
      ) : (
        <div className="space-y-2">
          {configs.map((c) => (
            <div key={c.consumer_id} className="text-[11px]">
              <div className="font-medium text-gray-700 dark:text-gray-300">{c.consumer_id}</div>
              {c.rules.map((r) => (
                <div key={r.rule_id} className="flex justify-between text-[10px] text-gray-400">
                  <span className="font-mono">{r.event_pattern}</span>
                  <span>→ {new URL(r.target_url).hostname}</span>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
