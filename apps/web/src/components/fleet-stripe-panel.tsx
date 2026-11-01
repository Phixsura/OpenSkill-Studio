"use client";
export function FleetStripePanel({ accounts, active, volume, successRate }: { accounts: number; active: number; volume: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💳 Stripe</h3>
    <div className="text-sm">{active}/{accounts} active · ${volume.toLocaleString()}/24h · {successRate}% success</div>
  </div>);
}
