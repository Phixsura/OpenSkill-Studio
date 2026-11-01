"use client";
export function FleetNatsPanel({ servers, connected, subscriptions, msgsPerSec }: { servers: number; connected: number; subscriptions: number; msgsPerSec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ NATS</h3>
    <div className="text-sm">{connected}/{servers} connected · {subscriptions.toLocaleString()} subs · {msgsPerSec.toLocaleString()} msg/s</div>
  </div>);
}
