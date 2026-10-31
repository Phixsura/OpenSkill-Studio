"use client";
export function FleetSnsPanel({ topics, messages, subscriptions, failedDeliveries }: { topics: number; messages: number; subscriptions: number; failedDeliveries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📢 SNS</h3>
    <div className="text-sm">{topics} topics · {messages.toLocaleString()} msgs · {subscriptions} subs</div>
    {failedDeliveries > 0 && <span className="text-xs text-red-500">⚠️ {failedDeliveries} failed</span>}
  </div>);
}
