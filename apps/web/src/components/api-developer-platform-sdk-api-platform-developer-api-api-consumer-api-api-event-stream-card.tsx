"use client";

interface SubInfo { subscription_id: string; consumer_id: string; transport: string; event_types: string[]; events_delivered: number; active: boolean; }
interface Props { subscriptions: SubInfo[]; activeCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEventStreamCard({ subscriptions, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Event Stream</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount} active</p>
        </div>
      </div>
      {subscriptions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No streams</p>
      ) : (
        <div className="space-y-1.5">
          {subscriptions.map((s) => (
            <div key={s.subscription_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
                <span className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{s.transport}</span>
              </div>
              <div className="text-[10px] text-gray-400">{s.event_types.join(", ")} · {s.events_delivered.toLocaleString()} delivered</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
