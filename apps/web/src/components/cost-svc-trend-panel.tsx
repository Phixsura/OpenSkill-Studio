"use client";
interface CostSvcTrendPanelProps { trend: string; changePct: number; current: number; }
export function CostSvcTrendPanel({ trend, changePct, current }: CostSvcTrendPanelProps) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Cost Trend</h3>
    <span className="text-xs">{trend} · {changePct > 0 ? "+" : ""}{changePct}% · ${current}</span>
  </div>);
}
