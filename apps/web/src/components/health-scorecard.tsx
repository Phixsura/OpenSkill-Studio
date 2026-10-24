"use client";

interface Dimension { dimension: string; score: number; target: number;
  weight: number; weighted: number; met: boolean; }
interface HealthScorecardProps { totalScore: number; grade: string;
  dimensions: Dimension[]; targetsMet: number; targetsTotal: number; }

const GRADE_COLORS: Record<string, string> = {
  "A+": "text-green-600", A: "text-green-600", B: "text-blue-600",
  C: "text-yellow-600", D: "text-red-600",
};

export function HealthScorecard({ totalScore, grade, dimensions, targetsMet, targetsTotal }: HealthScorecardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-6 text-center border-b dark:border-gray-700">
        <div className={`text-5xl font-bold ${GRADE_COLORS[grade] ?? ""}`}>{grade}</div>
        <div className="text-lg font-mono mt-1">{totalScore}/100</div>
        <div className="text-xs text-gray-400">{targetsMet}/{targetsTotal} targets met</div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {dimensions.map(d => (
          <div key={d.dimension} className="px-4 py-2.5">
            <div className="flex justify-between text-xs mb-0.5">
              <span className="capitalize">{d.dimension.replaceAll("_", " ")} {d.met ? "✅" : "⚠"}</span>
              <span>{d.score} / {d.target} (×{d.weight})</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${d.met ? "bg-green-500" : "bg-yellow-500"}`}
                style={{ width: `${Math.min(d.score, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
