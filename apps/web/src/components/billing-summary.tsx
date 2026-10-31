"use client";

interface Plan { name: string; price: number; interval: string; status: string; }
interface UsageItem { name: string; quantity: number; cost: number; }
interface Invoice { id: string; amount: number; status: string; date: string; }
interface BillingSummaryProps { plan: Plan; currentUsage: number; usageItems: UsageItem[]; invoices: Invoice[]; }

export function BillingSummary({ plan, currentUsage, usageItems, invoices }: BillingSummaryProps) {
  return (
    <div className="space-y-5">
      <div className="rounded-xl border p-4 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-lg font-bold">{plan.name}</p>
            <p className="text-sm text-gray-400">${plan.price}/{plan.interval}</p>
          </div>
          <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${plan.status === "active" ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-gray-100 text-gray-500"}`}>
            {plan.status}
          </span>
        </div>
      </div>
      <div>
        <h4 className="text-sm font-semibold mb-2">Current Usage: ${currentUsage.toFixed(2)}</h4>
        <div className="space-y-1">
          {usageItems.map(u => (
            <div key={u.name} className="flex justify-between text-sm">
              <span className="text-gray-500">{u.name} ({u.quantity.toLocaleString()})</span>
              <span>${u.cost.toFixed(2)}</span>
            </div>
          ))}
        </div>
      </div>
      <div>
        <h4 className="text-sm font-semibold mb-2">Recent Invoices</h4>
        <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
          {invoices.map(inv => (
            <div key={inv.id} className="flex items-center justify-between px-4 py-2 text-sm">
              <span className="font-mono text-xs text-gray-400">{inv.id}</span>
              <span>${inv.amount.toFixed(2)}</span>
              <span className="text-xs text-gray-400">{inv.date}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
