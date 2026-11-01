"use client";
export function FleetCiAnalyticsV9Panel({ pipelines, successRate }: { pipelines: number; successRate: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 CI Analytics v9</h3>
    <div className="text-sm">{pipelines} pipelines · {successRate}% success</div>
  </div>);
}
