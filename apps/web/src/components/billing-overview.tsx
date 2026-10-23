"use client";

interface BillingPlan { name: string; price: number; interval: string; }
interface CurrentPeriod { baseCost: number; overage: number; total: number; }
interface UsageSummary { apiCalls: number; apiLimit: number; apiPct: number; storageMb: number; }
interface BillingOverviewProps { plan: BillingPlan; currentPeriod: CurrentPeriod;
  usageSummary: UsageSummary; paymentMethod: { type: string; last4: string; brand: string } | null;
  onUpgrade: () => void; onManagePayment: () => void; }

export function BillingOverview({ plan, currentPeriod, usageSummary, paymentMethod, onUpgrade, onManagePayment }: BillingOverviewProps) {
  return (
    <div className="space-y-5">
      <div className="rounded-xl border p-5 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-400">Current Plan</p>
            <p className="text-lg font-bold">{plan.name}</p>
            <p className="text-sm text-gray-400">${plan.price}/{plan.interval}</p>
          </div>
          <button onClick={onUpgrade} className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white">Change Plan</button>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">${currentPeriod.total.toFixed(2)}</p>
          <p className="text-xs text-gray-400">Current Period</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{usageSummary.apiPct}%</p>
          <p className="text-xs text-gray-400">API Usage</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{usageSummary.storageMb}MB</p>
          <p className="text-xs text-gray-400">Storage</p>
        </div>
      </div>
      {paymentMethod && (
        <div className="flex items-center justify-between rounded-lg border px-4 py-3 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <span>💳</span>
            <span className="text-sm">{paymentMethod.brand} ••••{paymentMethod.last4}</span>
          </div>
          <button onClick={onManagePayment} className="text-xs text-blue-600 hover:underline">Manage</button>
        </div>
      )}
    </div>
  );
}
