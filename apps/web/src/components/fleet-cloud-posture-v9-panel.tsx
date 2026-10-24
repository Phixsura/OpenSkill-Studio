"use client";
export function FleetCloudPostureV9Panel({ accounts, score }: { accounts: number; score: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ Cloud Posture v9</h3>
    <div className="text-sm">{accounts} accounts · {score}/100 score</div>
  </div>);
}
