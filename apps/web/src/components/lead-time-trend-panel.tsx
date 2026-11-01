"use client";
interface LeadTimeTrendPanelProps { trend: string; recentAvg: number; olderAvg: number; }
const TC: Record<string, string> = { improving: "text-green-600", worsening: "text-red-500", stable: "text-gray-400" };
export function LeadTimeTrendPanel({ trend, recentAvg, olderAvg }: LeadTimeTrendPanelProps) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <div className="flex items-center justify-between mb-1"><h3 className="font-semibold">⏳ Lead Time Trend</h3>
      <span className={`text-xs font-bold ${TC[trend] ?? ""}`}>{trend}</span></div>
    <div className="grid grid-cols-2 gap-2 text-center text-xs">
      <div><span className="text-gray-400">Recent</span><div className="font-bold">{recentAvg}h</div></div>
      <div><span className="text-gray-400">Older</span><div className="font-bold">{olderAvg}h</div></div></div>
  </div>);
}
