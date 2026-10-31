"use client";

interface DeployScorecardProps { totalScore: number; grade: string;
  breakdown: Record<string, number>; }

const GRADE_COLORS: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-600" };

export function DeployScorecard({ totalScore, grade, breakdown }: DeployScorecardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-6 text-center border-b dark:border-gray-700">
        <div className={`text-5xl font-bold ${GRADE_COLORS[grade] ?? ""}`}>{grade}</div>
        <div className="text-lg font-mono mt-1">{totalScore}/100</div>
        <div className="text-xs text-gray-400">Deployment Scorecard</div>
      </div>
      <div className="p-4 space-y-2">
        {Object.entries(breakdown).map(([key, val]) => (
          <div key={key}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="capitalize">{key.replaceAll("_", " ")}</span>
              <span className="font-mono">{val}</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${val >= 80 ? "bg-green-500" : val >= 60 ? "bg-yellow-500" : "bg-red-500"}`}
                style={{ width: `${val}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
