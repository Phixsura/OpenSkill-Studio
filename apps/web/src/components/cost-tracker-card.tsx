"use client";

interface CostByCategory {
  category: string;
  amount: number;
}

interface BudgetAlert {
  category: string;
  spent: number;
  limit: number;
  pct: number;
}

interface CostTrackerCardProps {
  categories: CostByCategory[];
  alerts: BudgetAlert[];
  totalSpent: number;
  currency: string;
  appName: string;
}

export default function CostTrackerCard({
  categories,
  alerts,
  totalSpent,
  currency,
  appName,
}: CostTrackerCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            💰 Cost Tracker
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-gray-900 dark:text-gray-100">
          {currency} {totalSpent.toFixed(2)}
        </span>
      </div>

      {alerts.length > 0 && (
        <div className="mb-3 space-y-1">
          {alerts.map((a) => (
            <div
              key={a.category}
              className="rounded-lg bg-red-50 px-3 py-1.5 text-xs text-red-700 dark:bg-red-900/30 dark:text-red-300"
            >
              ⚠ {a.category}: {a.pct}% of budget ({currency} {a.spent.toFixed(2)} /{" "}
              {a.limit.toFixed(2)})
            </div>
          ))}
        </div>
      )}

      {categories.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No costs recorded</p>
      ) : (
        <div className="space-y-1.5">
          {categories.map((c) => {
            const pct = totalSpent > 0 ? Math.round((c.amount / totalSpent) * 100) : 0;
            return (
              <div
                key={c.category}
                className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                    {c.category}
                  </span>
                  <span className="text-[10px] text-gray-400">{pct}%</span>
                </div>
                <span className="font-mono text-xs text-gray-600 dark:text-gray-400">
                  {currency} {c.amount.toFixed(2)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
