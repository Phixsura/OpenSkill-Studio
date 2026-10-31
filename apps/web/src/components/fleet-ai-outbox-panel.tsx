"use client";
export function FleetAiOutboxPanel({ processors, active, messages, pending, published }: { processors: number; active: number; messages: number; pending: number; published: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📤 AI Outbox Processor</h3>
    <div className="text-sm">{active}/{processors} active · {messages.toLocaleString()} msgs · {pending} pending · {published.toLocaleString()} published</div>
  </div>);
}
