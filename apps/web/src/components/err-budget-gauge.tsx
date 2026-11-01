"use client";

interface ErrBudgetGaugeProps { consumedPct: number; remaining: number;
  allowed: number; action: string; exhausted: boolean;
  projectedAtEnd: number; dailyBurnPct: number; }

export function ErrBudgetGauge({ consumedPct, remaining, allowed, action, exhausted, projectedAtEnd, dailyBurnPct }: ErrBudgetGaugeProps) {
  const color = exhausted ? "bg-red-500" : consumedPct > 80 ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 Error Budget</h3>
        <span className={`text-xs font-medium ${exhausted ? "text-red-600" : consumedPct > 80 ? "text-yellow-600" : "text-green-600"}`}>
          {action === "freeze_deploys" ? "🚫 Deploy Freeze" : action === "caution" ? "⚠ Caution" : "✅ Normal"}
        </span>
      </div>
      <div className="p-4">
        <div className="flex justify-between text-xs mb-1">
          <span>Budget consumed</span>
          <span className="font-bold">{consumedPct}%</span>
        </div>
        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full">
          <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(consumedPct, 100)}%` }} />
        </div>
        <div className="flex justify-between text-[10px] text-gray-400 mt-1">
          <span>{remaining} remaining</span>
          <span>{allowed} allowed</span>
        </div>
      </div>
      <div className="px-4 py-2 border-t dark:border-gray-700 text-xs text-gray-400">
        Burn: {dailyBurnPct}%/day · Projected: {projectedAtEnd}% at window end
      </div>
    </div>
  );
}
