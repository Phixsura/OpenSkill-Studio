"use client";
export function FleetPubsubPanel({ topics, messages, subscriptions, backlog }: { topics: number; messages: number; subscriptions: number; backlog: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📨 Pub/Sub</h3>
    <div className="text-sm">{topics} topics · {messages.toLocaleString()} msgs · {subscriptions} subs</div>
    {backlog > 1000 && <span className="text-xs text-yellow-600">⚠️ {backlog.toLocaleString()} backlog</span>}
  </div>);
}
