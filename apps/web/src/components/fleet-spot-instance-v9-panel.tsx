"use client";
export function FleetSpotInstanceV9Panel({ instances, savings }: { instances: number; savings: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Spot Instance v9</h3>
    <div className="text-sm">{instances} instances · {savings}% savings</div>
  </div>);
}
