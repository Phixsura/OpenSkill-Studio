"use client";
export function FleetApiTimeoutV9Panel({ endpoints, timeouts }: { endpoints: number; timeouts: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏰ API Timeout v9</h3>
    <div className="text-sm">{endpoints} endpoints · {timeouts} timeouts today</div>
  </div>);
}
