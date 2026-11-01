"use client";

interface Sub { id: string; pattern: string; consumerId: string; active: boolean; }
interface Delivery { eventId: string; eventType: string; consumerId: string; timestamp: string; }
interface Props { subscriptions: Sub[]; recentDeliveries: Delivery[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEventBusCard({ subscriptions, recentDeliveries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Event Bus</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {subscriptions.length} subscriptions</p>
      </div>
      <div className="mb-3 space-y-1">
        {subscriptions.map((s) => (
          <div key={s.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
            <code className="text-blue-600 dark:text-blue-400">{s.pattern}</code>
            <span className={s.active ? "text-green-500" : "text-gray-400"}>{s.active ? "Active" : "Paused"}</span>
          </div>
        ))}
        {subscriptions.length === 0 && <p className="text-center text-sm text-gray-400">No subscriptions</p>}
      </div>
      {recentDeliveries.length > 0 && (
        <div>
          <div className="text-[10px] text-gray-400 mb-1">Recent deliveries:</div>
          {recentDeliveries.slice(0, 3).map((d) => (
            <div key={d.eventId} className="text-[9px] text-gray-500">{d.eventType} → {d.consumerId} · {d.timestamp}</div>
          ))}
        </div>
      )}
    </div>
  );
}
