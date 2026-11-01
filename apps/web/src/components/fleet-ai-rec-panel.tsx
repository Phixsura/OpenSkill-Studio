"use client";
export function FleetAiRecPanel({ services, active, recs, ctr }: { services: number; active: number; recs: number; ctr: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 AI Recommendations</h3>
    <div className="text-sm">{active}/{services} active · {recs.toLocaleString()} recs · {ctr}% CTR</div>
  </div>);
}
