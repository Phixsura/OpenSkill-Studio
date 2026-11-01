"use client";

interface Plan { name: string; price: number; interval: string; apiLimit: number; }
interface Usage { apiCalls: number; apiPct: number; storageMb: number; }
interface Billing { base: number; overage: number; total: number; }
interface Invoice { id: string; amount: number; status: string; date: string; }
interface BillingPageProps { orgName: string; plan: Plan; usage: Usage; billing: Billing;
  payment: { brand: string; last4: string } | null; invoices: Invoice[];
  onUpgrade: () => void; onManagePayment: () => void; }

export function BillingPage({ orgName, plan, usage, billing, payment, invoices,
  onUpgrade, onManagePayment }: BillingPageProps) {
  return (
    <div className="space-y-6">
      <h2 className="text-lg font-bold">💳 Billing — {orgName}</h2>
      <div className="rounded-xl border p-5 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-400">Current Plan</p>
            <p className="text-xl font-bold">{plan.name}</p>
            <p className="text-sm text-gray-400">${plan.price}/{plan.interval}</p>
          </div>
          <button onClick={onUpgrade} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Change Plan</button>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">${billing.total.toFixed(2)}</p>
          <p className="text-xs text-gray-400">Current Period</p>
        </div>
        <div className="rounded-xl border p-3 text-center dark:border-gray-700">
          <p className={`text-xl font-bold ${usage.apiPct > 100 ? "text-red-600" : ""}`}>{usage.apiPct}%</p>
          <p className="text-xs text-gray-400">API Usage</p>
        </div>
        <div className="rounded-xl border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{usage.storageMb}MB</p>
          <p className="text-xs text-gray-400">Storage</p>
        </div>
      </div>
      {billing.overage > 0 && (
        <p className="text-xs text-yellow-600">⚠ Overage charges: ${billing.overage.toFixed(2)}</p>
      )}
      {payment && (
        <div className="flex items-center justify-between rounded-lg border px-4 py-3 dark:border-gray-700">
          <span className="text-sm">💳 {payment.brand} ••••{payment.last4}</span>
          <button onClick={onManagePayment} className="text-xs text-blue-600">Manage</button>
        </div>
      )}
      <div>
        <h3 className="text-sm font-semibold mb-2">Recent Invoices</h3>
        <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
          {invoices.map(inv => (
            <div key={inv.id} className="flex items-center justify-between px-4 py-2 text-sm">
              <code className="text-xs text-gray-400">{inv.id}</code>
              <span>${inv.amount.toFixed(2)}</span>
              <span className="text-xs text-green-600">{inv.status}</span>
              <span className="text-xs text-gray-400">{inv.date}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
