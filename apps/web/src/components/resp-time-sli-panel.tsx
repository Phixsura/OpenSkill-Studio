"use client";
interface RespTimeSliPanelProps { sliPct: number; samples: number; thresholdMs: number;
  goodCount: number; badCount: number; trend: string; }
const TREND_COLOR: Record<string, string> = { improving: "text-green-600", degrading: "text-red-500", stable: "text-gray-400" };
export function RespTimeSliPanel({ sliPct, samples, thresholdMs, goodCount, badCount, trend }: RespTimeSliPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Response Time SLI</h3>
        <span className={`text-xs font-bold ${sliPct >= 99 ? "text-green-600" : sliPct >= 95 ? "text-yellow-600" : "text-red-500"}`}>
          {sliPct}% good ({thresholdMs}ms threshold)
        </span>
      </div>
      <div className="grid grid-cols-4 gap-2 p-4 text-center text-xs">
        <div><span className="text-gray-400">SLI</span><div className="font-bold text-lg">{sliPct}%</div></div>
        <div><span className="text-gray-400">Good</span><div className="font-bold text-green-600">{goodCount}</div></div>
        <div><span className="text-gray-400">Bad</span><div className={`font-bold ${badCount > 0 ? "text-red-500" : "text-gray-400"}`}>{badCount}</div></div>
        <div><span className="text-gray-400">Trend</span><div className={`font-bold ${TREND_COLOR[trend] ?? ""}`}>{trend}</div></div>
      </div>
    </div>
  );
}
