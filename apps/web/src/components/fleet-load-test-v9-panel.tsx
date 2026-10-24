"use client";
export function FleetLoadTestV9Panel({ tests, maxRps }: { tests: number; maxRps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏋️ Load Test v9</h3>
    <div className="text-sm">{tests} tests · {maxRps.toLocaleString()} max rps</div>
  </div>);
}
