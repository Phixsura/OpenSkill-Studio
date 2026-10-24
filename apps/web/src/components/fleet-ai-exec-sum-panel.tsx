"use client";
export function FleetAiExecSumPanel({ revenue, cost, margin, users, uptime }: { revenue: number; cost: number; margin: number; users: number; uptime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👔 AI Executive Summary</h3>
    <div className="text-sm">${revenue.toLocaleString()} rev · ${cost.toLocaleString()} cost · {margin}% margin · {users.toLocaleString()} users · {uptime}% uptime</div>
  </div>);
}
