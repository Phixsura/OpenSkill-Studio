"use client";

interface BillingAlert { past_due: boolean; near_limit: boolean; }
interface BillingPageLayoutProps {
  planName: string; planPrice: string; renewalDate: string | null;
  currentSpend: string; hasPaymentMethod: boolean; paymentLast4?: string | null;
  alerts: BillingAlert; onUpgrade: () => void; onAddPayment: () => void;
  children: React.ReactNode;
}

export function BillingPageLayout({ planName, planPrice, renewalDate, currentSpend, hasPaymentMethod, paymentLast4, alerts, onUpgrade, onAddPayment, children }: BillingPageLayoutProps) {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Billing</h1>
      {alerts.past_due && (
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700 dark:bg-red-900/20 dark:text-red-300">
          🚨 You have a past-due invoice. Please update your payment method.
        </div>
      )}
      {alerts.near_limit && (
        <div className="rounded-lg bg-yellow-50 p-3 text-sm text-yellow-700 dark:bg-yellow-900/20">
          ⚠️ Approaching usage limits. Consider upgrading your plan.
        </div>
      )}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <p className="text-xs text-gray-400">Current Plan</p>
          <p className="text-lg font-bold capitalize">{planName}</p>
          <p className="text-sm text-gray-500">{planPrice}</p>
          {renewalDate && <p className="text-xs text-gray-400">Renews {renewalDate}</p>}
          <button onClick={onUpgrade} className="mt-2 rounded bg-blue-600 px-3 py-1 text-xs text-white">Upgrade</button>
        </div>
        <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <p className="text-xs text-gray-400">Current Spend</p>
          <p className="text-2xl font-bold">{currentSpend}</p>
        </div>
        <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <p className="text-xs text-gray-400">Payment Method</p>
          {hasPaymentMethod ? (
            <p className="text-sm font-medium">💳 •••• {paymentLast4}</p>
          ) : (
            <button onClick={onAddPayment} className="mt-1 rounded border px-3 py-1 text-xs text-blue-600">Add Payment</button>
          )}
        </div>
      </div>
      <div>{children}</div>
    </div>
  );
}
