"use client";
export function FleetSqsPanel({ queues, visible, inFlight, dlqMessages }: { queues: number; visible: number; inFlight: number; dlqMessages: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📬 SQS</h3>
    <div className="text-sm">{queues} queues · {visible} visible · {inFlight} in-flight</div>
    {dlqMessages > 0 && <span className="text-xs text-red-500">💀 {dlqMessages} DLQ messages</span>}
  </div>);
}
