"use client";
export function FleetCodeReviewPanel({ totalPrs, reviewed, unreviewed, avgReviewHours, fast }: { totalPrs: number; reviewed: number; unreviewed: number; avgReviewHours: number; fast: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👀 Code Review</h3>
    <div className="text-sm">{reviewed}/{totalPrs} reviewed · avg {avgReviewHours}h</div>
    {unreviewed > 0 && <span className="text-xs text-yellow-600">⚠️ {unreviewed} unreviewed PRs</span>}
  </div>);
}
