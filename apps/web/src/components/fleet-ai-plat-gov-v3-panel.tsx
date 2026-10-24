"use client";
export function FleetAiPlatGovV3Panel({ frameworks, active, policies, reviews, compliance }: { frameworks: number; active: number; policies: number; reviews: number; compliance: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ AI Governance v3</h3>
    <div className="text-sm">{active}/{frameworks} active · {policies} policies · {reviews} reviews · {compliance}% compliance</div>
  </div>);
}
