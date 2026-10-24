"use client";
interface AlertFreqTrendPanelProps { trend: string; recentAvg: number; total: number; }
export function AlertFreqTrendPanel({ trend, recentAvg, total }: AlertFreqTrendPanelProps) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 Alert Frequency</h3>
    <span className="text-xs">{trend} · recent: {recentAvg}/period · {total} total</span>
  </div>);
}
