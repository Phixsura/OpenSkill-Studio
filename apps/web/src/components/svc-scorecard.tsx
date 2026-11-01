"use client";

interface Dimension { dimension: string; score: number; grade: string; }
interface SvcScorecardProps { service: string; dimensions: Dimension[];
  avgScore: number; overallGrade: string; }

const GRADE_COLORS: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-600" };

export function SvcScorecard({ service, dimensions, avgScore, overallGrade }: SvcScorecardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 {service}</h3>
        <div className="flex gap-2">
          <span className={`text-xl font-bold ${GRADE_COLORS[overallGrade] ?? ""}`}>{overallGrade}</span>
          <span className="text-xs text-gray-400 self-end">{avgScore}/100</span>
        </div>
      </div>
      <div className="p-3 space-y-1.5">
        {dimensions.map(d => (
          <div key={d.dimension}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="capitalize">{d.dimension}</span>
              <span className={GRADE_COLORS[d.grade] ?? ""}>{d.score} ({d.grade})</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${d.score >= 80 ? "bg-green-500" : d.score >= 60 ? "bg-yellow-500" : "bg-red-500"}`}
                style={{ width: `${d.score}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
