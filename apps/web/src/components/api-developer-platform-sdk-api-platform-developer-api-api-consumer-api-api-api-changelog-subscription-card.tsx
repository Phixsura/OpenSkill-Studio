"use client";

interface SubInfo { consumer_id: string; channels: string[]; active: boolean; notifications_sent: number; }
interface Props { subscriptions: SubInfo[]; activeCount: number; appName: string; }

const chIcon: Record<string, string> = { email: "📧", webhook: "🔗", in_app: "📱", slack: "💬" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiApiChangelogSubscriptionCard({ subscriptions, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📰 Changelog Subs</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount} active</p>
        </div>
      </div>
      {subscriptions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No subscriptions</p>
      ) : (
        <div className="space-y-1">
          {subscriptions.map((s) => (
            <div key={s.consumer_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1">
                <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
                {s.channels.map((c) => <span key={c}>{chIcon[c] ?? "•"}</span>)}
              </div>
              <span className="text-gray-400">{s.notifications_sent} sent</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
