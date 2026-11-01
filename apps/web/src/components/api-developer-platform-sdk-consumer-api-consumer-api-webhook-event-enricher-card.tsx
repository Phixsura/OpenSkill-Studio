"use client";

interface Rule { id: string; sourceType: string; targetField: string; value: string; }
interface Props { webhookId: string; rules: Rule[]; enabled: boolean; enrichedCount: number; consumerId: string; appName: string; }

const sourceColors: Record<string, string> = {
  static: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  lookup: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  computed: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
};

export default function APIDeveloperPlatformSDKConsumerApiConsumerApiWebhookEventEnricherCard({ webhookId, rules, enabled, enrichedCount, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✨ Event Enricher</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {webhookId}</p>
        </div>
        <span className={enabled ? "text-green-500 text-[10px]" : "text-gray-400 text-[10px]"}>{enabled ? "ON" : "OFF"}</span>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No enrichment rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.id} className="flex items-center gap-1 rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <span className={`rounded px-1 py-0.5 text-[9px] ${sourceColors[r.sourceType] ?? ""}`}>{r.sourceType}</span>
              <span className="text-gray-400">→</span>
              <code className="text-gray-700 dark:text-gray-300">{r.targetField}</code>
              {r.value && <span className="text-gray-400">= {r.value}</span>}
            </div>
          ))}
        </div>
      )}
      {enrichedCount > 0 && <div className="mt-2 text-[10px] text-gray-400">{enrichedCount} payloads enriched</div>}
    </div>
  );
}
