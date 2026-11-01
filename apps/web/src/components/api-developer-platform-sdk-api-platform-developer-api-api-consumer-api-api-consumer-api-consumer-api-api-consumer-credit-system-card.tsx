"use client";

interface Transaction { id: string; amount: number; balance: number; reason: string; timestamp: string; }
interface Props { balance: number; totalPurchased: number; totalConsumed: number; transactions: Transaction[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerCreditSystemCard({ balance, totalPurchased, totalConsumed, transactions, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💎 API Credits</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      <div className="mb-3 text-center">
        <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{balance.toLocaleString()}</div>
        <div className="text-[10px] text-gray-400">credits remaining</div>
      </div>
      <div className="mb-3 grid grid-cols-2 gap-2 text-center text-[11px]">
        <div className="rounded bg-green-50 p-1.5 dark:bg-green-900/20"><div className="font-bold text-green-600">+{totalPurchased.toLocaleString()}</div><div className="text-[10px] text-gray-400">Purchased</div></div>
        <div className="rounded bg-red-50 p-1.5 dark:bg-red-900/20"><div className="font-bold text-red-600">-{totalConsumed.toLocaleString()}</div><div className="text-[10px] text-gray-400">Consumed</div></div>
      </div>
      {transactions.length > 0 && (
        <div className="space-y-0.5">
          {transactions.slice(0, 5).map((t) => (
            <div key={t.id} className="flex justify-between text-[10px]">
              <span className="text-gray-500">{t.reason}</span>
              <span className={t.amount > 0 ? "text-green-500" : "text-red-500"}>{t.amount > 0 ? "+" : ""}{t.amount}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
