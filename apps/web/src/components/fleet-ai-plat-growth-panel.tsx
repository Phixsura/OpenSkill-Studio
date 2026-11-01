"use client";
export function FleetAiPlatGrowthPanel({ trackers, active, mau, mrr, growth, churn }: { trackers: number; active: number; mau: number; mrr: number; growth: number; churn: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Platform Growth</h3>
    <div className="text-sm">{active}/{trackers} active · {mau.toLocaleString()} MAU · ${mrr.toLocaleString()} MRR · +{growth}% growth · {churn}% churn</div>
  </div>);
}
