"use client";
export function FleetSendgridPanel({ accounts, active, emails, deliveryRate, bounceRate }: { accounts: number; active: number; emails: number; deliveryRate: number; bounceRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📧 SendGrid</h3>
    <div className="text-sm">{active}/{accounts} active · {emails.toLocaleString()} emails · {deliveryRate}% delivered</div>
  </div>);
}
