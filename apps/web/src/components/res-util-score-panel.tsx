"use client";
interface ResScore { name: string; score: number; status: string; cpuPct: number; memoryPct: number; }
interface ResUtilScorePanelProps { scores: ResScore[]; overallScore: number; }
const STATUS_COLOR: Record<string, string> = { optimal: "text-green-600", underused: "text-blue-500", overused: "text-red-500" };
export function ResUtilScorePanel({ scores, overallScore }: ResUtilScorePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Resource Utilization</h3>
        <span className="text-xs font-bold">Score: {overallScore}/100</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {scores.map(s => (
          <div key={s.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.name}</span>
            <span className={STATUS_COLOR[s.status] ?? ""}>
              {s.score}/100 · {s.status} · CPU {s.cpuPct}% · MEM {s.memoryPct}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
