"use client";
interface Subscription { id: string; url: string; events: string[]; deliveries: number; }
interface WhSubMgrPanelProps { subscriptions: Subscription[]; active: number; totalDeliveries: number; }
export function WhSubMgrPanel({ subscriptions, active, totalDeliveries }: WhSubMgrPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🪝 Webhook Subscriptions</h3>
        <span className="text-xs text-gray-400">{active} active · {totalDeliveries.toLocaleString()} deliveries</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {subscriptions.map(s => (
          <div key={s.id} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-mono truncate max-w-[200px]">{s.url}</span>
              <span className="text-gray-400">{s.deliveries} sent</span>
            </div>
            <div className="flex gap-1">{s.events.map(e => (
              <span key={e} className="px-1 rounded bg-gray-100 dark:bg-gray-800 text-[10px]">{e}</span>
            ))}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
