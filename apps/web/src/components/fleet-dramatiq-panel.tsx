"use client";
export function FleetDramatiqPanel({ brokers, online, messages, workers }: { brokers: number; online: number; messages: number; workers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎭 Dramatiq</h3>
    <div className="text-sm">{online}/{brokers} online · {messages.toLocaleString()} msgs · {workers} workers</div>
  </div>);
}
