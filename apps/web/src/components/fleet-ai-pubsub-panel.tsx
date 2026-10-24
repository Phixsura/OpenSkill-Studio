"use client";
export function FleetAiPubsubPanel({ systems, active, topics, subscriptions, messages }: { systems: number; active: number; topics: number; subscriptions: number; messages: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📢 AI PubSub</h3>
    <div className="text-sm">{active}/{systems} active · {topics} topics · {subscriptions} subs · {messages.toLocaleString()} msgs</div>
  </div>);
}
