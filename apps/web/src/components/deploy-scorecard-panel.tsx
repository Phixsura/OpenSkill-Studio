"use client";
interface DeployScorecardPanelProps { version: string; score: number; grade: string;
  deployReady: boolean; dimensions: Record<string, number>; }
const GRADE_COLOR: Record<string, string> = { A: "bg-green-500", B: "bg-blue-500", C: "bg-yellow-500", F: "bg-red-500" };
export function DeployScorecardPanel({ version, score, grade, deployReady, dimensions }: DeployScorecardPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-white text-center ${GRADE_COLOR[grade] ?? "bg-gray-500"}`}>
        <div className="text-2xl font-black">{score}/100 — {grade}</div>
        <div className="text-xs">{version} · {deployReady ? "✅ Deploy Ready" : "❌ Not Ready"}</div>
      </div>
      <div className="p-4 space-y-1">
        {Object.entries(dimensions).map(([dim, val]) => (
          <div key={dim} className="flex items-center gap-2 text-xs">
            <span>{val > 0 ? "✅" : "❌"}</span>
            <span className={val > 0 ? "" : "text-gray-400"}>{dim}</span>
            <span className="text-gray-400 ml-auto">{val}pts</span>
          </div>
        ))}
      </div>
    </div>
  );
}
