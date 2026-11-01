"use client";
export function FleetSlBudgetPanel({ total, exhausted, low, healthy, alert }: { total: number; exhausted: number; low: number; healthy: number; alert: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 SL Budget</h3>
    <div className="text-sm">🟢 {healthy} · 🟡 {low} low · 🔴 {exhausted} exhausted</div>
    {alert && <span className="text-xs text-red-500">🚨 Budget exhausted!</span>}
  </div>);
}
