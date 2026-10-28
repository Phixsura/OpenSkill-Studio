"use client";

interface SubscriptionInfo {
  subscription_id: string;
  url: string;
  event_pattern: string;
  enabled: boolean;
  delivery_count: number;
}

interface APIWebhookSubscriptionCardProps {
  subscriptions: SubscriptionInfo[];
  appName: string;
}

export default function APIWebhookSubscriptionCard({ subscriptions, appName }: APIWebhookSubscriptionCardProps) {
  const enabled = subscriptions.filter((s) => s.enabled).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Webhook Subscriptions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{enabled}/{subscriptions.length} active</span>
      </div>

      {subscriptions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No subscriptions</p>
      ) : (
        <div className="space-y-1.5">
          {subscriptions.map((s) => (
            <div key={s.subscription_id} className={`rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800 ${!s.enabled ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{s.event_pattern}</span>
                <span className="text-[10px] text-gray-400">{s.delivery_count} sent</span>
              </div>
              <p className="mt-0.5 truncate text-[10px] text-gray-400">{s.url}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
