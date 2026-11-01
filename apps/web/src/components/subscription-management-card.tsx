"use client";

interface SubscriptionManagementCardProps { plan: string; billingCycle: string;
  status: string; periodEnd: string; cancelAtEnd: boolean;
  onCancel: () => void; onUpgrade: () => void; onResume: () => void; }

export function SubscriptionManagementCard({ plan, billingCycle, status, periodEnd,
  cancelAtEnd, onCancel, onUpgrade, onResume }: SubscriptionManagementCardProps) {
  return (
    <div className="rounded-lg border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold capitalize">{plan} Plan</h3>
          <p className="text-xs capitalize text-gray-400">{billingCycle} billing</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${status === "active" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {status}
        </span>
      </div>
      <div className="mt-3 rounded bg-gray-50 p-3 dark:bg-gray-800">
        <p className="text-sm text-gray-500">
          {cancelAtEnd ? "⚠️ Cancels at end of period" : `Renews on ${new Date(periodEnd).toLocaleDateString()}`}
        </p>
      </div>
      <div className="mt-3 flex gap-2">
        <button onClick={onUpgrade} className="flex-1 rounded bg-blue-600 py-2 text-sm text-white">Upgrade</button>
        {cancelAtEnd ? (
          <button onClick={onResume} className="rounded border px-4 py-2 text-sm text-green-600 dark:border-gray-600">Resume</button>
        ) : status === "active" ? (
          <button onClick={onCancel} className="rounded border border-red-300 px-4 py-2 text-sm text-red-600">Cancel</button>
        ) : null}
      </div>
    </div>
  );
}
