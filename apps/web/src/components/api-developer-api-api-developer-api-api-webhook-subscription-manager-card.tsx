"use client";

interface SubInfo { subscription_id: string; topic: string; callback_url: string; active: boolean; deliveries: number; success_rate: number; }
interface Props { subscriptions: SubInfo[]; failingCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiWebhookSubscriptionManagerCard({ subscriptions, failingCount, appName }: Props) {
  const activeCount = subscriptions.filter(s => s.active).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📬 Subscriptions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount} active</p>
        </div>
        {failingCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{failingCount} failing</span>}
      </div>
      {subscriptions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No subscriptions</p>
      ) : (
        <div className="space-y-1.5">
          {subscriptions.map((s) => (
            <div key={s.subscription_id} className={`flex items-center justify-between text-[11px] ${s.active ? "" : "opacity-40"}`}>
              <div className="flex items-center gap-1.5">
                <span className="rounded bg-purple-50 px-1 py-0.5 text-[9px] text-purple-700 dark:bg-purple-900 dark:text-purple-200">{s.topic}</span>
                <span className="text-gray-400">→</span>
                <span className="text-gray-700 dark:text-gray-300">{new URL(s.callback_url).hostname}</span>
              </div>
              <span className="text-gray-400">{s.success_rate}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
