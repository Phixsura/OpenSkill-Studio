"use client";
export function FleetAiCodeRevPanel({ reviewers, active, prs, suggestions, accepted, acceptRate }: { reviewers: number; active: number; prs: number; suggestions: number; accepted: number; acceptRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔎 AI Code Review</h3>
    <div className="text-sm">{active}/{reviewers} active · {prs.toLocaleString()} PRs · {suggestions.toLocaleString()} suggestions · {acceptRate}% accepted</div>
  </div>);
}
