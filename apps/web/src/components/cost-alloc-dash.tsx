"use client";

interface TeamCost { team: string; cost: number; pct: number; }
interface CostAllocDashProps { totalCost: number; byTeam: TeamCost[];
  budget: number; actual: number; variancePct: number; status: string; }

const STATUS_STYLE: Record<string, string> = { under: "text-green-600", warning: "text-yellow-600", over: "text-red-500" };

export function CostAllocDash({ totalCost, byTeam, budget, actual, variancePct, status }: CostAllocDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💰 Cost Allocation</h3>
        <span className={`text-xs font-bold ${STATUS_STYLE[status] ?? ""}`}>
          ${totalCost.toLocaleString()}/mo · {variancePct > 0 ? "+" : ""}{variancePct}% vs budget
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Budget</div><div className="font-bold text-lg">${budget.toLocaleString()}</div></div>
        <div><div className="text-gray-400">Actual</div><div className={`font-bold text-lg ${STATUS_STYLE[status] ?? ""}`}>${actual.toLocaleString()}</div></div>
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {byTeam.map(t => (
          <div key={t.team} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-semibold">{t.team}</span>
            <span className="text-gray-400">${t.cost.toLocaleString()} ({t.pct}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
}
