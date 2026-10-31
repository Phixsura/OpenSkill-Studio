"use client";
export function FleetSagaPanel({ total, completed, compensating, failed, healthy }: { total: number; completed: number; compensating: number; failed: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Sagas</h3>
    <div className="text-sm">{completed}✅ {compensating}⏪ {failed}❌</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ Saga issues detected</span>}
  </div>);
}
