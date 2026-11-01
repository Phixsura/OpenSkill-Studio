"use client";
interface DeployCountTrendPanelProps { trend: string; recentAvg: number; olderAvg: number; }
export function DeployCountTrendPanel({ trend, recentAvg, olderAvg }: DeployCountTrendPanelProps) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Deploy Frequency</h3>
    <span className="text-xs">{trend} · recent: {recentAvg}/period · older: {olderAvg}/period</span>
  </div>);
}
