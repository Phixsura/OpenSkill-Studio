"use client";
interface ChangeDiffPanelProps { added: number; removed: number; changed: number; risk: string; totalDiffs: number; }
const RISK_STYLE: Record<string, string> = { high: "text-red-500", low: "text-green-600", none: "text-gray-400" };
export function ChangeDiffPanel({ added, removed, changed, risk, totalDiffs }: ChangeDiffPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 Change Diff</h3>
        <span className={`text-xs font-bold ${RISK_STYLE[risk] ?? ""}`}>{risk} risk · {totalDiffs} diffs</span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Added</span><div className="font-bold text-green-600 text-lg">+{added}</div></div>
        <div><span className="text-gray-400">Removed</span><div className="font-bold text-red-500 text-lg">-{removed}</div></div>
        <div><span className="text-gray-400">Changed</span><div className="font-bold text-yellow-600 text-lg">~{changed}</div></div>
      </div>
    </div>
  );
}
