"use client";
export function FleetCircleciPanel({ total, success, creditsUsed, successRate }: { total: number; success: number; creditsUsed: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⭕ CircleCI</h3>
    <div className="text-sm">{successRate}% success · {creditsUsed.toLocaleString()} credits · {total} workflows</div>
  </div>);
}
