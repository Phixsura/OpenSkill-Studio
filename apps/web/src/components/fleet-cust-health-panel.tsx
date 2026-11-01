"use client";
export function FleetCustHealthPanel({ total, healthy, atRisk, churning, healthRate }: { total: number; healthy: number; atRisk: number; churning: number; healthRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 Customer Health</h3>
    <div className="text-sm">🟢 {healthy} · 🟡 {atRisk} · 🔴 {churning} ({healthRate}% healthy)</div>
  </div>);
}
