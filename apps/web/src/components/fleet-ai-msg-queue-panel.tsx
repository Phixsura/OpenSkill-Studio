"use client";
export function FleetAiMsgQueuePanel({ queues, active, messages, dlq, latency }: { queues: number; active: number; messages: number; dlq: number; latency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📬 AI Message Queue</h3>
    <div className="text-sm">{active}/{queues} active · {messages.toLocaleString()} msgs · {dlq} DLQ · {latency}ms</div>
  </div>);
}
