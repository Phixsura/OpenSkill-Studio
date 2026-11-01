"use client";
export function FleetApiDataQualityV9Panel({ apis, score }: { apis: number; score: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Data Quality v9</h3>
    <div className="text-sm">{apis} APIs · {score}/100 quality</div>
  </div>);
}
