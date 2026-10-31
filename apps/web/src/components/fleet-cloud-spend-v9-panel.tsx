"use client";
export function FleetCloudSpendV9Panel({ providers, daily }: { providers: number; daily: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ Cloud Spend v9</h3>
    <div className="text-sm">{providers} providers · ${daily.toLocaleString()}/day</div>
  </div>);
}
