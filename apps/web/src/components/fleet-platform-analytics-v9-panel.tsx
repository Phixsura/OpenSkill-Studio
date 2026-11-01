"use client";
export function FleetPlatformAnalyticsV9Panel({ dau, apiCalls }: { dau: number; apiCalls: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Platform Analytics v9</h3>
    <div className="text-sm">{dau.toLocaleString()} DAU · {apiCalls.toLocaleString()} API calls</div>
  </div>);
}
