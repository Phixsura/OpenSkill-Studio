"use client";
export function FleetTechDebtPanel({ totalDebt, highDebt, avgPerService, manageable }: { totalDebt: number; highDebt: number; avgPerService: number; manageable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ Tech Debt</h3>
    <div className="text-sm">{totalDebt}h total · {avgPerService}h avg · {highDebt} high-debt</div>
    <span className={`text-xs ${manageable ? "text-green-600" : "text-red-500"}`}>{manageable ? "✅ Manageable" : "⚠️ High debt"}</span>
  </div>);
}
