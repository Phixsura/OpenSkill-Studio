"use client";

interface RuleInfo { rule_id: string; field_name: string; source: string; }
interface ConfigInfo { consumer_id: string; rules: RuleInfo[]; enabled: boolean; }
interface Props { configs: ConfigInfo[]; appName: string; }

const srcIcon: Record<string, string> = { static: "📌", lookup: "🔍", computed: "⚡", timestamp: "🕐", consumer_info: "👤" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventEnricherCard({ configs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✨ Event Enricher</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {configs.length} configs</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No enrichment configs</p>
      ) : (
        <div className="space-y-2">
          {configs.map((c) => (
            <div key={c.consumer_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
                <span className={c.enabled ? "text-green-600 dark:text-green-400" : "text-gray-400"}>{c.enabled ? "on" : "off"}</span>
              </div>
              <div className="flex flex-wrap gap-1 mt-0.5">
                {c.rules.map((r) => <span key={r.rule_id} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{srcIcon[r.source] ?? "•"} {r.field_name}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
