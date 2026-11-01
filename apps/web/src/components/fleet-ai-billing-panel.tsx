"use client";
export function FleetAiBillingPanel({ meters, active, revenue, invoices, customers }: { meters: number; active: number; revenue: number; invoices: number; customers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💳 AI Billing</h3>
    <div className="text-sm">{active}/{meters} active · ${revenue.toLocaleString()} rev · {invoices} invoices · {customers} customers</div>
  </div>);
}
