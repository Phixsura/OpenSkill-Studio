"use client";
export function FleetApiRetryV9Panel({ endpoints, retries }: { endpoints: number; retries: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔁 API Retry v9</h3>
    <div className="text-sm">{endpoints} endpoints · {retries} retries</div>
  </div>);
}
