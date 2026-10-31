"use client";
export function FleetWhRetryPanel({ totalRetries, recovered, exhausted, recoveryRate }: { totalRetries: number; recovered: number; exhausted: number; recoveryRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Webhook Retries</h3>
    <div className="text-sm">{totalRetries} retries · {recoveryRate}% recovered · {exhausted} exhausted</div>
  </div>);
}
