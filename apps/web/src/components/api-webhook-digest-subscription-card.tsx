"use client";

interface SubInfo { subscription_id: string; destination: string; frequency: string; enabled: boolean; digest_count: number; }
interface Props { subscriptions: SubInfo[]; appName: string; }

export default function APIWebhookDigestSubscriptionCard({ subscriptions, appName }: Props) {
  const active = subscriptions.filter((s) => s.enabled).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📬 Digest Subscriptions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{active}/{subscriptions.length} active</span>
      </div>
      {subscriptions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No digest subscriptions</p>
      ) : (
        <div className="space-y-1">
          {subscriptions.map((s) => (
            <div key={s.subscription_id} className={`flex items-center justify-between text-[11px] ${!s.enabled ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1.5">
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800">{s.frequency}</span>
                <span className="truncate max-w-[140px] text-gray-700 dark:text-gray-300">{s.destination}</span>
              </div>
              <span className="text-gray-400">{s.digest_count} sent</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
