"use client";
export function FleetResendPanel({ domains, verified, emails, deliveryRate }: { domains: number; verified: number; emails: number; deliveryRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📧 Resend</h3>
    <div className="text-sm">{verified}/{domains} verified · {emails.toLocaleString()} emails · {deliveryRate}%</div>
  </div>);
}
