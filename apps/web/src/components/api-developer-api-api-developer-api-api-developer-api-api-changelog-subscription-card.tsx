"use client";

interface SubInfo { subscription_id: string; developer_id: string; channels: string[]; filters: string[]; notifications_sent: number; active: boolean; }
interface Props { subscriptions: SubInfo[]; activeCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiChangelogSubscriptionCard({ subscriptions, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📢 Changelog Subscriptions</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount} active</p>
      </div>
      {subscriptions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No subscriptions</p>
      ) : (
        <div className="space-y-1.5">
          {subscriptions.map((s) => (
            <div key={s.subscription_id} className={`flex items-center justify-between text-[11px] ${s.active ? "" : "opacity-40"}`}>
              <div className="flex items-center gap-1">
                <span className="text-gray-700 dark:text-gray-300">{s.developer_id}</span>
                {s.channels.map((c) => <span key={c} className="rounded bg-blue-50 px-1 py-0.5 text-[9px] text-blue-700 dark:bg-blue-900 dark:text-blue-200">{c}</span>)}
              </div>
              <span className="text-gray-400">{s.notifications_sent} sent</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
