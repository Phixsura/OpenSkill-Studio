"use client";

interface TypeInfo { event_type: string; category: string; deprecated: boolean; subscriber_count: number; }
interface Props { types: TypeInfo[]; activeCount: number; deprecatedCount: number; appName: string; }

const catEmoji: Record<string, string> = { account: "👤", billing: "💳", order: "🛒", user: "👥", webhook: "🔔", system: "⚙️", security: "🔒", integration: "🔌" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventTypeRegistryCard({ types, activeCount, deprecatedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📚 Event Type Registry</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount} active</p>
        </div>
        {deprecatedCount > 0 && <span className="text-[10px] text-amber-600 dark:text-amber-400">⚠️ {deprecatedCount} deprecated</span>}
      </div>
      {types.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No event types</p>
      ) : (
        <div className="space-y-1">
          {types.map((t) => (
            <div key={t.event_type} className="flex items-center justify-between text-[11px]">
              <span className={t.deprecated ? "text-gray-400 line-through" : "font-mono text-gray-700 dark:text-gray-300"}>{catEmoji[t.category] ?? "•"} {t.event_type}</span>
              <span className="text-gray-400">{t.subscriber_count} subs</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
