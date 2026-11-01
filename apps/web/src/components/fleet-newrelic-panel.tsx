"use client";
export function FleetNewrelicPanel({ total, reporting, apdex, errorRate }: { total: number; reporting: number; apdex: number; errorRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🟢 New Relic</h3>
    <div className="text-sm">{reporting}/{total} reporting · Apdex {apdex} · {errorRate}% errors</div>
  </div>);
}
