"use client";
interface RateAnalyzePanelProps { rps: number; total: number; avgPerWindow: number;
  maxPerWindow: number; spikeDetected: boolean; }
export function RateAnalyzePanel({ rps, total, avgPerWindow, maxPerWindow, spikeDetected }: RateAnalyzePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Request Rate</h3>
        <span className={`text-xs font-bold ${spikeDetected ? "text-red-500" : "text-green-600"}`}>
          {rps} rps{spikeDetected ? " · ⚠ SPIKE" : ""} · {total.toLocaleString()} total
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Avg/Window</span><div className="font-bold text-lg">{avgPerWindow}</div></div>
        <div><span className="text-gray-400">Max/Window</span>
          <div className={`font-bold text-lg ${spikeDetected ? "text-red-500" : ""}`}>{maxPerWindow}</div></div>
      </div>
    </div>
  );
}
