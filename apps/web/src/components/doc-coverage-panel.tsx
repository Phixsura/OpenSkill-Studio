"use client";
interface DocCoveragePanelProps { overallPct: number; grade: string; scores: Record<string, number>; totalEndpoints: number; }
const GRADE_COLOR: Record<string, string> = { A: "text-green-600", B: "text-blue-500", C: "text-yellow-600", F: "text-red-500" };
export function DocCoveragePanel({ overallPct, grade, scores, totalEndpoints }: DocCoveragePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📖 Doc Coverage</h3>
        <div className="flex items-center gap-2">
          <span className="text-lg font-black">{overallPct}%</span>
          <span className={`text-lg font-black ${GRADE_COLOR[grade] ?? ""}`}>{grade}</span>
          <span className="text-xs text-gray-400">{totalEndpoints} endpoints</span>
        </div>
      </div>
      <div className="p-4 space-y-1.5">
        {Object.entries(scores).map(([k, v]) => (
          <div key={k}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="text-gray-500 capitalize">{k.replace("_", " ")}</span>
              <span className="text-gray-400">{v}%</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${v >= 80 ? "bg-green-500" : v >= 50 ? "bg-yellow-500" : "bg-red-500"}`}
                style={{ width: `${v}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
