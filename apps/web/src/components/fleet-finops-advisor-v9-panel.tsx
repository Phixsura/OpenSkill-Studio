"use client";
export function FleetFinopsAdvisorV9Panel({ total, savings }: { total: number; savings: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💵 FinOps Advisor v9</h3>
    <div className="text-sm">{total} recs · ${savings.toLocaleString()}/mo savings</div>
  </div>);
}
