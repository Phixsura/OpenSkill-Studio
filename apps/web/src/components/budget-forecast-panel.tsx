"use client";
interface BudgetForecastPanelProps { budgetTotal: number; consumed: number; remaining: number;
  pctConsumed: number; dailyBurn: number; daysLeft: number; willExhaust: boolean;
  action: string; urgency: string; }
const URG_STYLE: Record<string, string> = { critical: "text-red-600", high: "text-orange-500", medium: "text-yellow-600", low: "text-green-600" };
export function BudgetForecastPanel({ budgetTotal, consumed, remaining, pctConsumed, dailyBurn,
  daysLeft, willExhaust, action, urgency }: BudgetForecastPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔮 Budget Forecast</h3>
        <span className={`text-xs font-bold ${URG_STYLE[urgency] ?? ""}`}>
          {daysLeft}d left · {action.replace(/_/g, " ")}
        </span>
      </div>
      <div className="p-4">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-400">{pctConsumed}% consumed</span>
          <span className="text-gray-400">{remaining} remaining · {dailyBurn}/day</span>
        </div>
        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full">
          <div className={`h-full rounded-full ${willExhaust ? "bg-red-500" : "bg-green-500"}`}
            style={{ width: `${Math.min(pctConsumed, 100)}%` }} />
        </div>
      </div>
    </div>
  );
}
