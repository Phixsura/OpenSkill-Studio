"use client";

interface SubInfo { subscription_id: string; event_pattern: string; handler_url: string; events_received: number; }
interface Props { subscriptions: SubInfo[]; recentEventCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiEventBusCard({ subscriptions, recentEventCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚌 Event Bus</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{recentEventCount} events</span>
      </div>
      {subscriptions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No subscriptions</p>
      ) : (
        <div className="space-y-1.5">
          {subscriptions.map((s) => (
            <div key={s.subscription_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="rounded bg-purple-50 px-1 py-0.5 text-[9px] text-purple-700 dark:bg-purple-900 dark:text-purple-200">{s.event_pattern}</span>
                <span className="text-gray-400">→</span>
                <span className="text-gray-700 dark:text-gray-300">{new URL(s.handler_url).hostname}</span>
              </div>
              <span className="text-gray-400">{s.events_received}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
