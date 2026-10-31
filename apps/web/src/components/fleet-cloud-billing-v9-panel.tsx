"use client";
export function FleetCloudBillingV9Panel({ accounts, spend }: { accounts: number; spend: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💳 Cloud Billing v9</h3>
    <div className="text-sm">{accounts} accounts · ${spend.toLocaleString()}/mo</div>
  </div>);
}
