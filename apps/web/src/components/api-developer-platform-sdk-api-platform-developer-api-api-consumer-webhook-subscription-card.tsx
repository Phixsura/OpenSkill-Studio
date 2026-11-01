"use client";

interface SubInfo { subscription_id: string; consumer_id: string; url: string; events: string[]; active: boolean; }
interface Props { subscriptions: SubInfo[]; activeCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerWebhookSubscriptionCard({ subscriptions, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Subscriptions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount} active</p>
        </div>
      </div>
      {subscriptions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No subscriptions</p>
      ) : (
        <div className="space-y-1.5">
          {subscriptions.map((s) => (
            <div key={s.subscription_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
                <span className={s.active ? "text-green-600 dark:text-green-400" : "text-gray-400"}>{s.active ? "● active" : "○ paused"}</span>
              </div>
              <div className="flex flex-wrap gap-1 mt-0.5">
                {s.events.map((e) => <span key={e} className="rounded bg-blue-100 px-1 text-[9px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{e}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
