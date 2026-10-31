"use client";
export function FleetDlqPanel({ queues, totalMessages, nonEmpty, clean }: { queues: number; totalMessages: number; nonEmpty: number; clean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💀 Dead Letter Queues</h3>
    {clean ? <span className="text-xs text-green-600">✅ All {queues} DLQs empty</span>
     : <span className="text-xs text-yellow-600">⚠️ {totalMessages.toLocaleString()} msgs in {nonEmpty} DLQs</span>}
  </div>);
}
