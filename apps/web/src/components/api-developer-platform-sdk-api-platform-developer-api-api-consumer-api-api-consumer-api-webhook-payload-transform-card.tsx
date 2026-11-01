"use client";

interface Rule { rule_id: string; source: string; target: string; }
interface Props { configId: string; webhookId: string; rules: Rule[]; dropUnmapped: boolean; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookPayloadTransformCard({ configId, webhookId, rules, dropUnmapped, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Payload Transform</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {webhookId}</p>
      </div>
      <div className="mb-2 flex items-center gap-2 text-[11px]">
        <span className="text-gray-500">Mode:</span>
        <span className={`rounded px-1.5 py-0.5 font-medium ${dropUnmapped ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400" : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"}`}>
          {dropUnmapped ? "Strict (drop unmapped)" : "Passthrough"}
        </span>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No transform rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center gap-1 rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <code className="text-blue-600 dark:text-blue-400">{r.source}</code>
              <span className="text-gray-400">→</span>
              <code className="text-green-600 dark:text-green-400">{r.target}</code>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
