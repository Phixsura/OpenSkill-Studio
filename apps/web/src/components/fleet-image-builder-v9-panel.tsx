"use client";
export function FleetImageBuilderV9Panel({ builds, avgTime }: { builds: number; avgTime: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ Image Builder v9</h3>
    <div className="text-sm">{builds} builds · {avgTime}s avg</div>
  </div>);
}
