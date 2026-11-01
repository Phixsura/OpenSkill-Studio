"use client";
export function FleetCostForecastPanel({ daily, monthly, annual, budgetWarning }: { daily: number; monthly: number; annual: number; budgetWarning: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Cost Forecast</h3>
    <div className="text-sm">${daily.toLocaleString()}/day · ${monthly.toLocaleString()}/mo · ${annual.toLocaleString()}/yr</div>
    {budgetWarning && <span className="text-xs text-yellow-600">⚠️ Over $50K/month</span>}
  </div>);
}
