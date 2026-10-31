"use client";

interface Rule { id: string; pattern: string; webhookUrl: string; priority: number; active: boolean; }
interface Props { rules: Rule[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookEventRouterCard({ rules, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔀 Event Router</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {rules.length} rules</p>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No routing rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.id} className={`flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800 ${!r.active ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1">
                <code className="text-blue-600 dark:text-blue-400">{r.pattern}</code>
                <span className="text-gray-400">→</span>
                <span className="truncate text-gray-500">{new URL(r.webhookUrl).hostname}</span>
              </div>
              <span className="text-gray-400">P{r.priority}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
