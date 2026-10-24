"use client";
export function FleetServicebusPanel({ namespaces, active, messages, dlqCount }: { namespaces: number; active: number; messages: number; dlqCount: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚌 Service Bus</h3>
    <div className="text-sm">{active}/{namespaces} active · {messages.toLocaleString()} msgs</div>
    {dlqCount > 0 && <span className="text-xs text-red-500">💀 {dlqCount} DLQ</span>}
  </div>);
}
