"use client";
export function FleetClusterSecurityV9Panel({ clusters, score }: { clusters: number; score: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ Cluster Security v9</h3>
    <div className="text-sm">{clusters} clusters · {score}/100 score</div>
  </div>);
}
