"use client";
export function FleetCodeReviewV9Panel({ total, avgHours }: { total: number; avgHours: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👀 Code Review v9</h3>
    <div className="text-sm">{total} reviews · {avgHours}h avg</div>
  </div>);
}
