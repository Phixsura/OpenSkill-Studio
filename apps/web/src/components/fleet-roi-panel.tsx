"use client";
export function FleetRoiPanel({ investment, totalReturn, roiPct, paybackMonths, positive }: { investment: number; totalReturn: number; roiPct: number; paybackMonths: number; positive: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Platform ROI</h3>
    <div className={`text-lg font-bold ${positive ? "text-green-600" : "text-red-500"}`}>{roiPct}% ROI</div>
    <div className="text-xs text-gray-400">${totalReturn.toLocaleString()} return · {paybackMonths}mo payback</div>
  </div>);
}
