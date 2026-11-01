"use client";

interface Invoice { invoiceId: string; amountCents: number; status: string; description: string; createdAt: number; }
interface Sub { planId: string; status: string; currentPeriodEnd: number; }

const statusColors: Record<string, string> = {
  paid: "text-green-600", pending: "text-yellow-600", overdue: "text-red-600", cancelled: "text-gray-400",
};

export function BillingPortalPage({ subscription, invoices, onCancel, onPay }: {
  subscription: Sub | null; invoices: Invoice[];
  onCancel?: () => void; onPay?: (invoiceId: string) => void;
}) {
  return (
    <div className="space-y-4">
      {subscription && (
        <div className="border dark:border-gray-700 rounded-xl p-4">
          <div className="flex justify-between items-center">
            <div>
              <span className="font-bold text-sm">Current Plan: {subscription.planId}</span>
              <span className={`text-xs ml-2 capitalize ${subscription.status === "active" ? "text-green-600" : "text-red-600"}`}>{subscription.status}</span>
            </div>
            {subscription.status === "active" && (
              <button onClick={onCancel} className="text-xs text-red-400">Cancel</button>
            )}
          </div>
        </div>
      )}
      <div>
        <h3 className="font-bold text-sm mb-2">Invoices</h3>
        {invoices.length === 0 ? (
          <div className="text-center text-gray-400 py-4 text-sm">No invoices</div>
        ) : (
          <div className="space-y-1">
            {invoices.map(inv => (
              <div key={inv.invoiceId} className="flex items-center justify-between border dark:border-gray-700 rounded-lg p-2.5 text-sm">
                <div>
                  <span className="font-medium">${(inv.amountCents / 100).toFixed(2)}</span>
                  <span className="text-xs text-gray-500 ml-2">{inv.description || inv.invoiceId}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs capitalize ${statusColors[inv.status] || ""}`}>{inv.status}</span>
                  {inv.status === "pending" && <button onClick={() => onPay?.(inv.invoiceId)} className="text-xs bg-blue-500 text-white px-2 py-1 rounded">Pay</button>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
