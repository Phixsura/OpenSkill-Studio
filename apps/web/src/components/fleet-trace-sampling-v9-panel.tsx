"use client";
export function FleetTraceSamplingV9Panel({ strategies, rate }: { strategies: number; rate: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Trace Sampling v9</h3>
    <div className="text-sm">{strategies} strategies · {rate}% sample rate</div>
  </div>);
}
