"use client";
interface HealthScorecardProps { overall: number; grade: string; dimensions: Record<string, number>; weakest: string; }
const GRADE_COLOR: Record<string, string> = { A: "text-green-600", B: "text-blue-500", C: "text-yellow-600", F: "text-red-600" };
export function HealthScorecard({ overall, grade, dimensions, weakest }: HealthScorecardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💯 Health Scorecard</h3>
        <div className="flex items-center gap-2">
          <span className="text-lg font-black">{overall}</span>
          <span className={`text-lg font-black ${GRADE_COLOR[grade] ?? ""}`}>{grade}</span>
        </div>
      </div>
      <div className="p-4 space-y-1">
        {Object.entries(dimensions).map(([dim, score]) => (
          <div key={dim} className="flex items-center gap-2 text-xs">
            <span className={`w-20 ${dim === weakest ? "text-red-500 font-bold" : "text-gray-500"}`}>{dim}</span>
            <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${score >= 90 ? "bg-green-500" : score >= 70 ? "bg-yellow-500" : "bg-red-500"}`} style={{ width: `${score}%` }} />
            </div>
            <span className="text-gray-400 w-8 text-right">{score}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
