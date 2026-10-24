"use client";
export function FleetAiBatchPanel({ total, completed, running, itemsProcessed }: { total: number; completed: number; running: number; itemsProcessed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ AI Batch</h3>
    <div className="text-sm">{completed}✅ {running}🔄 of {total} · {itemsProcessed.toLocaleString()} items</div>
  </div>);
}
