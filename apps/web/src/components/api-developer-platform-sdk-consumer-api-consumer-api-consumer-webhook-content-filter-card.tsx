"use client";

interface Rule { id: string; field: string; operator: string; value: string; }
interface Props { webhookId: string; rules: Rule[]; matchMode: string; consumerId: string; appName: string; }

const opColors: Record<string, string> = {
  equals: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  contains: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  not_equals: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  regex: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  exists: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  not_exists: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400",
};

export default function APIDeveloperPlatformSDKConsumerApiConsumerApiConsumerWebhookContentFilterCard({ webhookId, rules, matchMode, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Content Filter</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {webhookId} · Match: {matchMode.toUpperCase()}</p>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No filter rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.id} className="flex items-center gap-1 rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <code className="text-gray-700 dark:text-gray-300">{r.field}</code>
              <span className={`rounded px-1 py-0.5 text-[9px] ${opColors[r.operator] ?? ""}`}>{r.operator}</span>
              {r.value && <span className="text-gray-500">{r.value}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
