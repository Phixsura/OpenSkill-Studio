"use client";

interface Subscription {
  id: string;
  extensionName: string;
  extensionIcon: string;
  planName: string;
  price: number;
  currency: string;
  period: string;
  status: "active" | "trial" | "canceled" | "past_due";
  currentPeriodEnd: string;
  usageThisMonth: number;
  usageLimit: number;
}

export function SubscriptionManagementPanel({
  subscriptions,
  onCancel,
  onUpgrade,
}: {
  subscriptions: Subscription[];
  onCancel?: (id: string) => void;
  onUpgrade?: (id: string) => void;
}) {
  const totalMonthly = subscriptions
    .filter((s) => s.status === "active" || s.status === "trial")
    .reduce((sum, s) => sum + s.price, 0);

  const statusBadge: Record<string, { color: string; label: string }> = {
    active: { color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300", label: "Active" },
    trial: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300", label: "Trial" },
    canceled: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300", label: "Canceled" },
    past_due: { color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300", label: "Past Due" },
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">💳 Subscriptions</h2>
        <div className="text-sm text-gray-500">
          Monthly total: <span className="font-bold text-green-600">${(totalMonthly / 100).toFixed(2)}</span>
        </div>
      </div>

      <div className="space-y-3">
        {subscriptions.map((sub) => {
          const badge = statusBadge[sub.status];
          const usagePercent = Math.min(100, Math.round((sub.usageThisMonth / Math.max(1, sub.usageLimit)) * 100));
          return (
            <div key={sub.id} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{sub.extensionIcon}</span>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{sub.extensionName}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${badge.color}`}>{badge.label}</span>
                    </div>
                    <div className="text-sm text-gray-500">
                      {sub.planName} · ${(sub.price / 100).toFixed(2)}/{sub.period}
                    </div>
                    <div className="text-xs text-gray-400 mt-0.5">
                      Renews: {sub.currentPeriodEnd}
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  {sub.status === "active" && (
                    <>
                      <button onClick={() => onUpgrade?.(sub.id)} className="text-xs text-blue-500 hover:underline">Upgrade</button>
                      <button onClick={() => onCancel?.(sub.id)} className="text-xs text-red-500 hover:underline">Cancel</button>
                    </>
                  )}
                </div>
              </div>
              {sub.usageLimit > 0 && (
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>Usage: {sub.usageThisMonth.toLocaleString()} / {sub.usageLimit.toLocaleString()}</span>
                    <span>{usagePercent}%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                    <div className={`h-1.5 rounded-full ${usagePercent > 90 ? "bg-red-500" : "bg-blue-500"}`}
                         style={{ width: `${usagePercent}%` }} />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
