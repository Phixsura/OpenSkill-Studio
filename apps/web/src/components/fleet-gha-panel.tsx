"use client";
export function FleetGhaPanel({ total, success, failure, billableMin, successRate }: { total: number; success: number; failure: number; billableMin: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐙 GitHub Actions</h3>
    <div className="text-sm">{successRate}% success · {billableMin} min billed · {total} runs</div>
  </div>);
}
