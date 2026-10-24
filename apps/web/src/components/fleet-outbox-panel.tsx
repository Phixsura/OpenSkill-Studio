"use client";
export function FleetOutboxPanel({ tables, pending, processed, stuck, healthy }: { tables: number; pending: number; processed: number; stuck: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📤 Outbox</h3>
    <div className="text-sm">{pending} pending · {processed.toLocaleString()} processed/24h</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {stuck} stuck outboxes</span>}
  </div>);
}
