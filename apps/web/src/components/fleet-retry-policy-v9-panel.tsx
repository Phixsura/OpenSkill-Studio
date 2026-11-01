"use client";
export function FleetRetryPolicyV9Panel({ policies, retries }: { policies: number; retries: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔁 Retry Policy v9</h3>
    <div className="text-sm">{policies} policies · {retries} retries today</div>
  </div>);
}
