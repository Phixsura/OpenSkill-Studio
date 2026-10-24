"use client";
export function FleetAiGovernancePanel({ frameworks, active, policies, reviews }: { frameworks: number; active: number; policies: number; reviews: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ AI Governance</h3>
    <div className="text-sm">{active}/{frameworks} active · {policies} policies · {reviews.toLocaleString()} reviews</div>
  </div>);
}
