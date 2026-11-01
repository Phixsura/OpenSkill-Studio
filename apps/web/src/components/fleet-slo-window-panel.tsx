"use client";
export function FleetSloWindowPanel({ target, burnRate, budgetRemaining, alert }: { target: number; burnRate: number; budgetRemaining: number; alert: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 SLO Burn Window</h3>
    <div className="text-sm">Target: {(target * 100).toFixed(1)}% · Burn: {burnRate}x · Budget: {budgetRemaining}%</div>
    {alert && <span className="text-xs text-red-500">🚨 Budget burning fast!</span>}
  </div>);
}
